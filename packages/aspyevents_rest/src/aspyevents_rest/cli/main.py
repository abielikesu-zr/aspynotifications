import click
import structlog
from aspyevents_rest.api.rest_server_runner import AspyEventsRestServerRunner
from aspyrest.cli.rest_server import rest_start_command
from aspyevents_rest.api.main import events_rest_app

logger = structlog.get_logger(__name__)


@click.group()
def cli() -> None:
    pass


cli.add_command(
    rest_start_command(
        runner=AspyEventsRestServerRunner,
        app=events_rest_app,
    )
)

if __name__ == "__main__":
    cli()
