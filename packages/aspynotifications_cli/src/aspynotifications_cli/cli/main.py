import asyncio
from collections.abc import Callable
from typing import Any

import click
from aspylogger.services.logging_setup import bootstrap_logging

from aspynotifications_cli.cli.create_email_destination_handler import (
    create_email_destination_handler,
)
from aspynotifications_cli.cli.create_output_hole_destination_handler import (
    create_output_hole_destination_handler,
)
from aspynotifications_cli.cli.create_slack_channel_destination_handler import (
    create_slack_channel_destination_handler,
)
from aspynotifications_cli.cli.create_notification_policy_handler import (
    create_notification_policy_handler,
)
from aspynotifications_cli.cli.create_shole_provider_handler import (
    create_shole_provider_handler,
)
from aspynotifications_cli.cli.create_slack_provider_handler import (
    create_slack_provider_handler,
)
from aspynotifications_cli.cli.create_zeptomail_provider_handler import (
    create_zeptomail_provider_handler,
)
from aspynotifications_cli.cli.create_template_handler import create_template_handler
from aspynotifications_cli.cli.send_event_handler import send_event_handler


@click.group()
def cli() -> None:
    pass


def common_logging_options(func: Callable[..., Any]) -> Callable[..., Any]:
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


@click.command("create-slack-provider")
@click.option("--name", required=True)
@click.option("--webhook-url", required=True)
@common_logging_options
def create_slack_provider(
    name: str,
    webhook_url: str,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_slack_provider_handler(
            name=name,
            webhook_url=webhook_url,
            output_format=output_format,
        )
    )


@click.command("create-zeptomail-provider")
@click.option("--name", required=True)
@click.option("--from-address", required=True)
@click.option("--from-name")
@click.option("--send-mail-token", required=True)
@common_logging_options
def create_zeptomail_provider(
    name: str,
    from_address: str,
    from_name: str | None,
    send_mail_token: str,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_zeptomail_provider_handler(
            name=name,
            from_address=from_address,
            from_name=from_name,
            send_mail_token=send_mail_token,
            output_format=output_format,
        )
    )


@click.command("create-shole-provider")
@click.option("--name", required=True)
@click.option("--level", default="WARN", show_default=True)
@click.option("--cows/--no-cows", default=True)
@common_logging_options
def create_shole_provider(
    name: str,
    level: str,
    cows: bool,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_shole_provider_handler(
            name=name,
            level=level,
            cows=cows,
            output_format=output_format,
        )
    )


@click.command("create-template")
@click.option("--name", required=True)
@click.option("--email-subject-inline")
@click.option("--email-html-inline")
@click.option("--email-text-inline")
@click.option("--slack-blocks-inline")
@click.option("--output-hole-dumpster-inline")
@common_logging_options
def create_template(
    name: str,
    email_subject_inline: str | None,
    email_html_inline: str | None,
    email_text_inline: str | None,
    slack_blocks_inline: str | None,
    output_hole_dumpster_inline: str | None,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_template_handler(
            name=name,
            email_subject_inline=email_subject_inline,
            email_html_inline=email_html_inline,
            email_text_inline=email_text_inline,
            slack_blocks_inline=slack_blocks_inline,
            output_hole_dumpster_inline=output_hole_dumpster_inline,
            output_format=output_format,
        )
    )


@click.command("create-email-destination")
@click.option("--name", required=True)
@click.option("--provider", required=True)
@click.option("--template", required=True)
@click.option("--routable/--not-routable", default=False)
@click.option("--to", multiple=True)
@click.option("--cc", multiple=True)
@click.option("--bcc", multiple=True)
@common_logging_options
def create_email_destination(
    name: str,
    provider: str,
    template: str,
    routable: bool,
    to: tuple[str, ...],
    cc: tuple[str, ...],
    bcc: tuple[str, ...],
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_email_destination_handler(
            name=name,
            provider=provider,
            template=template,
            routable=routable,
            to=to,
            cc=cc,
            bcc=bcc,
            output_format=output_format,
        )
    )


@click.command("create-slack-channel-destination")
@click.option("--name", required=True)
@click.option("--provider", required=True)
@click.option("--template", required=True)
@click.option("--routable/--not-routable", default=False)
@click.option("--channel-id", required=True)
@common_logging_options
def create_slack_channel_destination(
    name: str,
    provider: str,
    template: str,
    routable: bool,
    channel_id: str,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_slack_channel_destination_handler(
            name=name,
            provider=provider,
            template=template,
            routable=routable,
            channel_id=channel_id,
            output_format=output_format,
        )
    )


@click.command("create-output-hole-destination")
@click.option("--name", required=True)
@click.option("--provider", required=True)
@click.option("--template", required=True)
@click.option("--routable/--not-routable", default=False)
@common_logging_options
def create_output_hole_destination(
    name: str,
    provider: str,
    template: str,
    routable: bool,
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_output_hole_destination_handler(
            name=name,
            provider=provider,
            template=template,
            routable=routable,
            output_format=output_format,
        )
    )


@click.command("create-policy")
@click.option("--name", required=True)
@click.option("--subject", required=True)
@click.option("--destination", "destinations", multiple=True, required=True)
@click.option("--envelope-policy", type=(str, str, str), multiple=True)
@click.option("--negative-envelope-policy", type=(str, str, str), multiple=True)
@click.option("--destination-policy", type=(str, str, str), multiple=True)
@click.option("--negative-destination-policy", type=(str, str, str), multiple=True)
@common_logging_options
def create_policy(
    name: str,
    subject: str,
    destinations: tuple[str, ...],
    envelope_policy: tuple[tuple[str, str, str], ...],
    negative_envelope_policy: tuple[tuple[str, str, str], ...],
    destination_policy: tuple[tuple[str, str, str], ...],
    negative_destination_policy: tuple[tuple[str, str, str], ...],
    output_format: str,
    verbose: int,
    quiet: int,
    log_format: str,
) -> None:
    bootstrap_logging(verbose=verbose, log_format=log_format, quiet=quiet)
    asyncio.run(
        create_notification_policy_handler(
            name=name,
            subject=subject,
            destinations=destinations,
            envelope_policy=envelope_policy,
            negative_envelope_policy=negative_envelope_policy,
            destination_policy=destination_policy,
            negative_destination_policy=negative_destination_policy,
            output_format=output_format,
        )
    )


cli.add_command(create_slack_provider)
cli.add_command(create_zeptomail_provider)
cli.add_command(create_shole_provider)
cli.add_command(create_template)
cli.add_command(create_email_destination)
cli.add_command(create_slack_channel_destination)
cli.add_command(create_output_hole_destination)
cli.add_command(create_policy)


if __name__ == "__main__":
    cli()
