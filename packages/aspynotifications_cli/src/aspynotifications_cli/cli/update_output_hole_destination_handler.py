import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.noop_dtos import OutputHoleDestinationConfigDTO
from aspynotifications_dtos.notifications_dtos import UpdateDestinationRequest
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def update_output_hole_destination_handler(
    destination_id: str,
    provider: str,
    template: str,
    output_format: str,
) -> None:
    log = logger.bind(function="update_output_hole_destination_handler")

    load_aspynotifications_cli_config()
    configure_logging()
    result = await get_notifications_sdk().update_destination(
        UpdateDestinationRequest(
            id=destination_id,
            provider=provider,
            template=template,
            config=OutputHoleDestinationConfigDTO(),
        )
    )
    data = result.model_dump(mode="json")
    log.info(
        "update_output_hole_destination_handler",
        destination_id=destination_id,
    )
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Updated output hole destination: {data['name']} ({data['id']})")
