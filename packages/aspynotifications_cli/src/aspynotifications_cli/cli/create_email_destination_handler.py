import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    EmailDestinationConfigDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def create_email_destination_handler(
    name: str,
    provider: str,
    template: str,
    to: tuple[str, ...],
    cc: tuple[str, ...],
    bcc: tuple[str, ...],
    output_format: str,
) -> None:
    log = logger.bind(function="create_email_destination_handler")

    load_aspynotifications_cli_config()
    configure_logging()
    result = await get_notifications_sdk().create_destination(
        CreateDestinationRequest(
            name=name,
            provider=provider,
            template=template,
            config=EmailDestinationConfigDTO(
                to=list(to),
                cc=list(cc),
                bcc=list(bcc),
            ),
        )
    )
    data = result.model_dump(mode="json")
    log.info("create_email_destination_handler")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created email destination: {data['name']} ({data['id']})")
