import json
from typing import Literal

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    CreateTemplateRequest,
    VSCodeTemplateDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def create_vscode_template_handler(
    name: str,
    title_inline: str,
    message_inline: str,
    severity: Literal["info", "warning", "error"],
    output_format: str,
) -> None:
    load_aspynotifications_cli_config()
    configure_logging()

    result = await get_notifications_sdk().create_template(
        CreateTemplateRequest(
            name=name,
            vscode=VSCodeTemplateDTO(
                title=TemplateSourceDTO(inline=title_inline),
                message=TemplateSourceDTO(inline=message_inline),
                severity=severity,
            ),
        )
    )
    data = result.model_dump(mode="json")
    logger.info("vscode_template_created", name=name)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created VS Code template: {data['name']}")
