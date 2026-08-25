import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    SlackTemplateDTO,
    UpdateTemplateRequest,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def update_template_handler(
    name: str,
    slack_blocks_inline: str,
    output_format: str,
) -> None:
    log = logger.bind(function="update_template_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    request = UpdateTemplateRequest(
        name=name,
        slack=SlackTemplateDTO(
            blocks=TemplateSourceDTO(inline=slack_blocks_inline)
        ),
    )
    result = await get_notifications_sdk().update_template(request)
    data = result.model_dump(mode="json")
    log.info("update_template_handler")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Updated template: {data['name']}")
