# aspyevents_worker/cli/worker.py

from __future__ import annotations

import asyncio

import click
import structlog
from aspylogger.services.logging_setup import bootstrap_logging

from aspyevents_worker.runner.base_worker_runner import BaseWorkerRunner

logger = structlog.get_logger(__name__)

PACKAGE_NAME = __package__ or ""


async def run_worker(
    runner: BaseWorkerRunner,
    config_file: str | None,
    nats_url: str | None = None,
) -> None:
    runner.load_config(
        config_file=config_file,
        nats_url=nats_url,
    )

    await runner.run()


@click.group("worker")
def worker() -> None:
    """Worker commands."""


@worker.command("start")
@click.option(
    "--verbose",
    "-v",
    count=True,
    help=(
        "Increase verbosity. "
        "-v: DEBUG for the application package. "
        "-vv: also raise the root logger to INFO."
    ),
)
@click.option(
    "--quiet",
    "-q",
    count=True,
    help=(
        "Decrease verbosity. "
        "-q: WARNING for the application package. "
        "-qq: also raise the root logger to WARNING."
    ),
)
@click.option(
    "--log-format",
    type=click.Choice(
        ["json", "console"],
        case_sensitive=False,
    ),
    default=None,
    help="Logging format: json or console. Defaults to console.",
)
@click.option(
    "--nats-url",
    default=None,
    help="NATS server URL.",
)
@click.option(
    "--configfile",
    help="Configuration file path.",
)
def start_worker(
    verbose: int,
    quiet: int,
    log_format: str | None,
    configfile: str | None,
    nats_url: str | None = None,
) -> None:
    """Start the worker."""

    context = click.get_current_context()

    runner_class = context.obj["runner"]
    worker_factory = context.obj["worker_factory"]

    runner = runner_class(
        worker_factory=worker_factory,
    )

    root_package = runner.get_package_name()
    my_package_name = (PACKAGE_NAME or "").split(".")[0]
    root_packages = [root_package, my_package_name]

    bootstrap_logging(
        verbose=verbose,
        quiet=quiet,
        log_format=log_format,
        root_package=root_packages,
    )

    try:
        asyncio.run(
            run_worker(
                runner=runner,
                config_file=configfile,
                nats_url=nats_url,
            )
        )

    except Exception as exc:
        logger.error(
            "Failed to start worker",
            error=str(exc),
            exc_info=exc,
        )

        raise click.ClickException(f"Failed to start worker: {exc}") from exc


def worker_start_command(
    *,
    runner: type[BaseWorkerRunner],
    worker_factory,
) -> click.Command:
    """
    Create a configured worker command group.
    """

    command = worker

    command.context_settings = {
        "obj": {
            "runner": runner,
            "worker_factory": worker_factory,
        }
    }

    return command
