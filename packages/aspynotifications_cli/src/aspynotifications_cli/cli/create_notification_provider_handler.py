import json

from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.noop_dtos import AHoleProviderDTO, AHoleProviderSettingsDTO
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    SlackProviderDTO,
    SlackProviderSettingsDTO,
    ZeptoMailCredentialsDTO,
    ZeptoMailProviderDTO,
    ZeptoMailProviderSettingsDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config


async def create_notification_provider_handler(
    name: str,
    provider_type: str,
    webhook_url: str | None,
    from_address: str | None,
    from_name: str | None,
    send_mail_token: str | None,
    level: str,
    cows: bool,
    output_format: str,
) -> None:
    load_aspynotifications_cli_config()
    configure_logging()

    if provider_type == "SLACK":
        provider = SlackProviderDTO(
            config=SlackProviderSettingsDTO(webhook_url=webhook_url),
        )
    elif provider_type == "ZEPTOMAIL":
        provider = ZeptoMailProviderDTO(
            config=ZeptoMailProviderSettingsDTO(
                from_address=from_address,
                from_name=from_name,
                credentials=ZeptoMailCredentialsDTO(send_mail_token=send_mail_token),
            )
        )
    else:
        provider = AHoleProviderDTO(config=AHoleProviderSettingsDTO(level=level, cows=cows))

    result = await get_notifications_sdk().create_notification_provider(
        CreateNotificationProviderRequest(name=name, provider=provider)
    )
    data = result.model_dump(mode="json")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created notification provider: {data['name']} ({data['id']})")
