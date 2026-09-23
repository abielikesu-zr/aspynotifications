import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import (
    UpdateDestinationRequest,
    VSCodeDestinationConfigDTO,
    VSCodeUserAudienceDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def update_vscode_destination_handler(
    destination_id: str,
    provider: str,
    template: str,
    recipient_user_id: str,
    output_format: str,
) -> None:
    load_aspynotifications_cli_config()
    configure_logging()

    result = await get_notifications_sdk().update_destination(
        UpdateDestinationRequest(
            id=destination_id,
            provider=provider,
            template=template,
            config=VSCodeDestinationConfigDTO(
                audience=VSCodeUserAudienceDTO(recipient_user_id=recipient_user_id)
            ),
        )
    )
    data = result.model_dump(mode="json")
    logger.info("vscode_destination_updated", destination_id=destination_id)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Updated VS Code destination: {data['name']} ({data['id']})")
