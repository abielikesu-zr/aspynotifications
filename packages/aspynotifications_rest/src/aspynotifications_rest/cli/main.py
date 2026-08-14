import click
import structlog
from aspyrest.cli.rest_server import rest_start_command

from aspynotifications_rest.api.main import notifications_rest_app
from aspynotifications_rest.api.rest_server_runner import (
    AspyNotificationsRestServerRunner,
)

logger = structlog.get_logger(__name__)


@click.group()
def cli() -> None:
    pass


cli.add_command(
    rest_start_command(
        runner=AspyNotificationsRestServerRunner,
        app=notifications_rest_app,
    )
)

if __name__ == "__main__":
    cli()
