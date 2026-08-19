import argparse
import asyncio
from pathlib import Path
from typing import Any

import yaml
from aspyconfig import get_config
from aspylogger.services.logging_setup import bootstrap_logging
from aspynotifications_dtos.notify_request import CreateNotifyRequest
from aspynotifications_sdk import get_notifications_sdk


def load_cases(source_files: list[Path]) -> list[dict[str, Any]]:
    """Load notification test cases from the configured YAML files."""
    cases: list[dict[str, Any]] = []

    for source_file in source_files:
        with source_file.open(encoding="utf-8") as source:
            source_data = yaml.safe_load(source) or {}

        file_cases = source_data["cases"]
        if not isinstance(file_cases, list):
            raise ValueError(f"'cases' must be a list in {source_file}")

        cases.extend(file_cases)

    return cases


async def main(source_files: list[Path]) -> None:
    bootstrap_logging(verbose=0)
    config = get_config()
    config.register_files(
        "mono",
        [
            "monoconfig/default/aspynotifications_sdk",
            "monoconfig/zrp0/aspynotifications_sdk",
        ],
    )
    config.load()

    notifications_sdk = get_notifications_sdk()

    for case in load_cases(source_files):
        case["event"].setdefault("data", {}).setdefault("context", {})[
            "test_origin"
        ] = "notify_test_sdk_from_file.py"

        print()
        print("=" * 60)
        print(f"Testing: {case['name']}")
        print("=" * 60)

        request = CreateNotifyRequest.model_validate({"event": case["event"]})
        result = await notifications_sdk.notify(request)
        print(f"Notification status → {result}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--notification-source",
        action="append",
        type=Path,
        required=True,
        help="YAML file containing notification test cases; repeat for multiple files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    asyncio.run(main(arguments.notification_source))
