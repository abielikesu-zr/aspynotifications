import click
from aspyevents_worker.cli.worker import worker_start_command

from aspynotifications_worker import get_notifications_worker
from aspynotifications_worker.runner.notifications_worker_runner import (
    NotificationsWorkerRunner,
)


@click.group()
def cli() -> None:
    """Aspy Notifications Worker CLI."""


cli.add_command(
    worker_start_command(
        runner=NotificationsWorkerRunner,
        worker_factory=get_notifications_worker,
    )
)


if __name__ == "__main__":
    cli()
