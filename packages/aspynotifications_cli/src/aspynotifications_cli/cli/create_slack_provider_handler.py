import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    SlackProviderDTO,
    SlackProviderSettingsDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def create_slack_provider_handler(
    name: str,
    webhook_url: str,
    output_format: str,
) -> None:
    log = logger.bind(function="create_slack_provider_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    result = await get_notifications_sdk().create_notification_provider(
        CreateNotificationProviderRequest(
            name=name,
            provider=SlackProviderDTO(
                config=SlackProviderSettingsDTO(webhook_url=webhook_url)
            ),
        )
    )
    data = result.model_dump(mode="json")
    log.info("create_slack_provider_handler")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created Slack provider: {data['name']} ({data['id']})")
