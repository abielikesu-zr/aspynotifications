import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.noop_dtos import AHoleProviderDTO, AHoleProviderSettingsDTO
from aspynotifications_dtos.providers_dtos import UpdateNotificationProviderRequest
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def update_shole_provider_handler(
    provider_id: str,
    level: str,
    cows: bool,
    output_format: str,
) -> None:
    log = logger.bind(function="update_shole_provider_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    result = await get_notifications_sdk().update_notification_provider(
        UpdateNotificationProviderRequest(
            id=provider_id,
            provider=AHoleProviderDTO(
                config=AHoleProviderSettingsDTO(level=level, cows=cows)
            ),
        )
    )
    data = result.model_dump(mode="json")
    log.info("update_shole_provider_handler", provider_id=provider_id)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Updated SHOLE provider: {data['name']} ({data['id']})")
