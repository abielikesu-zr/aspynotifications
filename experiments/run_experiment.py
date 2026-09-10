from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import yaml
from aspyconfig import get_config as aspy_get_config
from aspyconfig.utils.os_utils import get_os_username
from aspylogger.services.logging_setup import bootstrap_logging
from aspyevents_dtos.cloud_event_dto import CloudEventDTO, EventDataDTO
from aspyevents_dtos.publish_event_request import PublishEventRequest
from aspyevents_sdk import get_events_sdk
from aspynotifications import get_notification_facade
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.exceptions import ResourceAlreadyExistsError
from aspynotifications_dtos.noop_dtos import (
    AHoleProviderDTO,
    AHoleProviderSettingsDTO,
    BHoleTemplateDTO,
    OutputHoleDestinationConfigDTO,
)
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
)
from aspynotifications_dtos.providers_dtos import CreateNotificationProviderRequest
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = Path(__file__).resolve().parent / "cases"
SCORE_DIR = Path(__file__).resolve().parent / "score"
WORKER_LOG = REPO_ROOT / "notifications_worker.log"


def load_config() -> None:
    config = aspy_get_config()

    user_config_paths = [
        "monoconfig/default/aspynotifications_worker",
        "monoconfig/default/aspyevents_rest",
    ]
    local_config_paths = []
    username = get_os_username()
    if username:
        local_config_paths.append(f"monoconfig/{username}/aspynotifications_worker")
        local_config_paths.append(f"monoconfig/{username}/aspyevents_rest")

    config.register_common_config(
        cli_config=None,
        app_defaults=None,
        user_config_paths=user_config_paths,
        local_config_paths=local_config_paths,
    )
    config.load()


def load_experiments(cases_dir: Path) -> list[dict]:
    return [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(cases_dir.glob("*.yaml"))
    ]


def get_scenarios(cfg: dict) -> list[dict]:
    if "scenarios" in cfg:
        return cfg["scenarios"]
    return [{"name": cfg["event"]["type"], "flow": cfg.get("flow", {}), "event": cfg["event"]}]


def config_matches(cfg: dict, query: str | None) -> bool:
    if not query:
        return True
    if cfg.get("experiment_id") == query:
        return True
    for scenario in get_scenarios(cfg):
        if scenario.get("name") == query or scenario["event"].get("type") == query:
            return True
    return False


async def _create_ignoring_exists(coro, label: str) -> None:
    try:
        await coro
    except ResourceAlreadyExistsError:
        print(f"  (already exists, skip) {label}")


async def setup(flow: dict, seen: set[str]) -> None:
    facade = get_notification_facade()

    provider = flow.get("provider")
    if provider and f"provider:{provider['name']}" not in seen:
        seen.add(f"provider:{provider['name']}")
        await _create_ignoring_exists(
            facade.create_notification_provider(
                CreateNotificationProviderRequest(
                    name=provider["name"],
                    provider=AHoleProviderDTO(
                        config=AHoleProviderSettingsDTO(
                            level=provider.get("level", "WARN"),
                            cows=provider.get("cows", True),
                        )
                    ),
                )
            ),
            "provider",
        )

    template = flow.get("template")
    if template and f"template:{template['name']}" not in seen:
        seen.add(f"template:{template['name']}")
        await _create_ignoring_exists(
            facade.create_template(
                CreateTemplateRequest(
                    name=template["name"],
                    output_hole=BHoleTemplateDTO(
                        dumpster=TemplateSourceDTO(inline=template["dumpster_inline"])
                    ),
                )
            ),
            "template",
        )

    destination = flow.get("destination")
    if destination and f"destination:{destination['name']}" not in seen:
        seen.add(f"destination:{destination['name']}")
        await _create_ignoring_exists(
            facade.create_destination(
                CreateDestinationRequest(
                    name=destination["name"],
                    provider=destination["provider"],
                    template=destination["template"],
                    config=OutputHoleDestinationConfigDTO(),
                )
            ),
            "destination",
        )

    policy = flow.get("policy")
    if policy and f"policy:{policy['name']}" not in seen:
        seen.add(f"policy:{policy['name']}")
        await _create_ignoring_exists(
            facade.create_notification_policy(
                CreateNotificationPolicyRequest(
                    name=policy["name"],
                    subject=policy["subject"],
                    destinations=list(policy["destinations"]),
                )
            ),
            "policy",
        )


async def publish_event(event: dict) -> str:
    data = event.get("data", {})
    context = dict(data.get("context") or {})
    test_id = context.get("test_id") or str(uuid.uuid4())
    context["test_id"] = test_id

    cloud_event = CloudEventDTO(
        type=event["type"],
        source=event["source"],
        subject=event.get("subject"),
        data=EventDataDTO(
            event=data.get("event"),
            context=context,
        ),
    )

    await get_events_sdk().publish(PublishEventRequest(event=cloud_event))
    return test_id


async def setup_all(experiments: list[dict]) -> None:
    seen: set[str] = set()
    for cfg in experiments:
        for scenario in get_scenarios(cfg):
            print(f"Setup: {cfg['experiment_id']} / {scenario.get('name', '')}")
            await setup(scenario.get("flow", {}), seen)


async def publish_all(experiments: list[dict]) -> list[dict]:
    published: list[dict] = []
    for cfg in experiments:
        for scenario in get_scenarios(cfg):
            event = scenario["event"]
            test_id = await publish_event(event)
            print(
                f"  published '{cfg['experiment_id']}' / '{scenario.get('name', '')}' "
                f"test_id={test_id} type={event['type']}"
            )
            published.append(
                {
                    "experiment_id": cfg["experiment_id"],
                    "scenario": scenario.get("name"),
                    "test_id": test_id,
                    "event": event,
                }
            )
    return published


def run_check(case: dict, test_id: str, content: str) -> bool:
    check = case.get("check", "match_test_id")
    if check == "match_test_id":
        return test_id in content
    if check == "match_text":
        return str(case.get("text", "")) in content
    return False


def wait_for_delivery(test_ids: list[str], timeout: float = 10.0) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        content = WORKER_LOG.read_text(encoding="utf-8") if WORKER_LOG.exists() else ""
        if all(tid in content for tid in test_ids):
            return content
        time.sleep(0.5)
    return WORKER_LOG.read_text(encoding="utf-8") if WORKER_LOG.exists() else ""


def start_service(
    cmd: list[str],
    log_name: str | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.Popen:
    if log_name:
        log = open(REPO_ROOT / log_name, "a", encoding="utf-8")
    else:
        log = subprocess.DEVNULL
    env = None
    if extra_env:
        env = {**os.environ, **extra_env}
    return subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=env,
    )


def stop_service(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()


def save_result(result: dict, run_id: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{result['experiment_id']}_{timestamp}_{run_id}.json"
    path = SCORE_DIR / filename
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path


def cmd_run(args: argparse.Namespace) -> int:
    experiments = load_experiments(Path(args.cases_dir))
    experiments = [c for c in experiments if config_matches(c, args.experiment)]
    if not experiments:
        print("No experiments found.")
        return 1

    run_id = uuid.uuid4().hex[:8]

    procs: list[subprocess.Popen] = []
    try:
        bootstrap_logging(verbose=2)

        print("Starting NATS...")
        subprocess.run(["bash", "./nats.sh", "start"], cwd=REPO_ROOT, check=True)

        print("Starting notifications-rest...")
        procs.append(
            start_service(
                ["notifications-rest", "start", "--log-format", "json", "--log-file", "notifications_rest.log"]
            )
        )

        print("Starting aspyevents_rest...")
        procs.append(start_service(["aspyevents_rest", "start"], "aspyevents_rest.log"))

        load_config()
        shutil.rmtree(REPO_ROOT / "var" / "all_stores", ignore_errors=True)
        asyncio.run(setup_all(experiments))

        WORKER_LOG.write_text("", encoding="utf-8")

        print("Starting notifications-worker...")
        procs.append(
            start_service(
                ["notifications-worker", "start", "--log-format", "json"],
                "notifications_worker.log",
                extra_env={"ASPY_DEBUG": "aspynotifications:INFO"},
            )
        )

        time.sleep(3)

        published = asyncio.run(publish_all(experiments))
        test_ids = [p["test_id"] for p in published]
        content = wait_for_delivery(test_ids)

        grouped: dict[str, list[dict]] = {}
        for p in published:
            cases = []
            passed = failed = 0
            for case in p["event"].get("cases", []):
                ok = run_check(case, p["test_id"], content)
                cases.append(
                    {
                        "name": case.get("name"),
                        "check": case.get("check"),
                        "passed": ok,
                    }
                )
                if ok:
                    passed += 1
                else:
                    failed += 1

            grouped.setdefault(p["experiment_id"], []).append(
                {
                    "name": p["scenario"],
                    "event": {
                        "type": p["event"]["type"],
                        "source": p["event"].get("source"),
                        "subject": p["event"].get("subject"),
                    },
                    "test_id": p["test_id"],
                    "cases": cases,
                    "summary": {"total": len(cases), "passed": passed, "failed": failed},
                }
            )

        results: list[dict] = []
        for experiment_id, scenarios in grouped.items():
            result = {
                "experiment_id": experiment_id,
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(),
                "scenarios": scenarios,
            }
            results.append(result)
            path = save_result(result, run_id)
            print(f"  saved -> {path}")

        print("\nResults:")
        console = Console()
        display_results(console, results)
    finally:
        print("Stopping services...")
        for proc in procs:
            stop_service(proc)
        subprocess.run(["bash", "./nats.sh", "stop"], cwd=REPO_ROOT)
        print("All services stopped.")

    return 0


def _iter_scenarios(data: dict) -> list[dict]:
    if "scenarios" in data:
        return data["scenarios"]
    return [data]


def display_results(console: Console, data_list: list[dict]) -> None:
    table = Table(box=box.ROUNDED, expand=True, show_header=True)
    table.add_column("Test", style="bold", no_wrap=False)
    table.add_column("Case", no_wrap=False)
    table.add_column("Check", style="dim")
    table.add_column("Result", justify="center")

    total = passed = failed = 0
    for data in data_list:
        for scenario in _iter_scenarios(data):
            summary = scenario["summary"]
            total += summary["total"]
            passed += summary["passed"]
            failed += summary["failed"]

            test_label = scenario.get("name") or scenario["event"]["type"]
            for case in scenario["cases"]:
                result_text = "[green]PASS[/green]" if case["passed"] else "[red]FAIL[/red]"
                table.add_row(test_label, case["name"], case.get("check", ""), result_text)

    color = "green" if failed == 0 else "red"
    summary_text = (
        f"[{color}]● {total} cases — {passed} passed, {failed} failed[/{color}]"
    )

    console.print(
        Panel(table, title="[bold]Notification Experiments[/bold]", border_style=color)
    )
    console.print(f"  {summary_text}\n")


def cmd_report(args: argparse.Namespace) -> int:
    console = Console()

    files = sorted(SCORE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        console.print("[yellow]No results found in score/.[/yellow]")
        return 0

    latest: dict[str, dict] = {}
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        latest[data["experiment_id"]] = data

    experiments = list(latest.values())
    if args.experiment:
        experiments = [
            d
            for d in experiments
            if d["experiment_id"] == args.experiment
            or any(
                sc.get("name") == args.experiment
                or sc["event"].get("type") == args.experiment
                for sc in _iter_scenarios(d)
            )
        ]

    display_results(console, experiments)

    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="run_experiment.py")
    parser.add_argument("--cases-dir", default=str(CASES_DIR))
    parser.add_argument("--experiment", default=None)
    parser.add_argument(
        "command",
        nargs="?",
        choices=["run", "report"],
        default="run",
        help="Comando: 'run' (default) o 'report'.",
    )

    args = parser.parse_args(argv)

    if args.command == "run":
        return cmd_run(args)
    if args.command == "report":
        return cmd_report(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
