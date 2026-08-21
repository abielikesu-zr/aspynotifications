import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    ZeptoMailCredentialsDTO,
    ZeptoMailProviderDTO,
    ZeptoMailProviderSettingsDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def create_zeptomail_provider_handler(
    name: str,
    from_address: str,
    from_name: str | None,
    send_mail_token: str,
    output_format: str,
) -> None:
    log = logger.bind(function="create_zeptomail_provider_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    result = await get_notifications_sdk().create_notification_provider(
        CreateNotificationProviderRequest(
            name=name,
            provider=ZeptoMailProviderDTO(
                config=ZeptoMailProviderSettingsDTO(
                    from_address=from_address,
                    from_name=from_name,
                    credentials=ZeptoMailCredentialsDTO(
                        send_mail_token=send_mail_token
                    ),
                )
            ),
        )
    )
    data = result.model_dump(mode="json")
    log.info("create_zeptomail_provider_handler")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created ZeptoMail provider: {data['name']} ({data['id']})")
