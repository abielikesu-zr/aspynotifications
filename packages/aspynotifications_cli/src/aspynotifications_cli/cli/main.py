import asyncio

import click
from aspylogger.services.logging_setup import bootstrap_logging

from aspynotifications_cli.cli.send_event_handler import send_event_handler


@click.group()
def cli() -> None:
    pass


def common_logging_options(func):
    func = click.option(
        "--output-format",
        type=click.Choice(["print", "json"]),
        default="print",
    )(func)
    func = click.option(
        "--log-format",
        type=click.Choice(["plain", "json"]),
        default="plain",
    )(func)
    func = click.option("-q", "--quiet", count=True)(func)
    func = click.option("-v", "--verbose", count=True)(func)
    return func


@click.command("send-event")
@click.option(
    "--from-file",
    "file_path",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
)
@common_logging_options
def send_event(
    file_path: str,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(
        verbose=verbose,
        log_format=log_format,
        quiet=quiet,
    )

    asyncio.run(
        send_event_handler(
            file_path=file_path,
            output_format=output_format,
        )
    )


cli.add_command(send_event)


if __name__ == "__main__":
    cli()
