import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.providers_dtos import (
    UpdateNotificationProviderRequest,
    VSCodeProviderDTO,
    VSCodeProviderSettingsDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def update_vscode_provider_handler(
    provider_id: str,
    relay_url: str,
    output_format: str,
) -> None:
    load_aspynotifications_cli_config()
    configure_logging()

    result = await get_notifications_sdk().update_notification_provider(
        UpdateNotificationProviderRequest(
            id=provider_id,
            provider=VSCodeProviderDTO(
                config=VSCodeProviderSettingsDTO(relay_url=relay_url)
            ),
        )
    )
    data = result.model_dump(mode="json")
    logger.info("vscode_provider_updated", provider_id=provider_id)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Updated VS Code provider: {data['name']} ({data['id']})")
