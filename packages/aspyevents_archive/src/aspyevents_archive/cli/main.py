import click
from aspyevents_worker.cli.worker import worker_start_command

from aspyevents_archive import get_events_archive_worker
from aspyevents_archive.runner.archive_worker_runner import ArchiveWorkerRunner


@click.group()
def cli() -> None:
    """Events Archive Worker CLI."""


cli.add_command(
    worker_start_command(
        runner=ArchiveWorkerRunner,
        worker_factory=get_events_archive_worker,
    )
)


if __name__ == "__main__":
    cli()
