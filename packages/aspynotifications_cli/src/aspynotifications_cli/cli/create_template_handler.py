import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    CreateTemplateRequest,
    EmailTemplateDTO,
    SlackTemplateDTO,
)
from aspynotifications_dtos.noop_dtos import BHoleTemplateDTO
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def create_template_handler(
    name: str,
    email_subject_inline: str | None,
    email_html_inline: str | None,
    email_text_inline: str | None,
    slack_blocks_inline: str | None,
    output_hole_dumpster_inline: str | None,
    output_format: str,
) -> None:
    log = logger.bind(function="create_template_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    email = None
    if any((email_subject_inline, email_html_inline, email_text_inline)):
        email = EmailTemplateDTO(
            subject=TemplateSourceDTO(inline=email_subject_inline),
            html=TemplateSourceDTO(inline=email_html_inline),
            text=TemplateSourceDTO(inline=email_text_inline),
        )

    request = CreateTemplateRequest(
        name=name,
        email=email,
        slack=(
            SlackTemplateDTO(blocks=TemplateSourceDTO(inline=slack_blocks_inline))
            if slack_blocks_inline is not None
            else None
        ),
        output_hole=(
            BHoleTemplateDTO(
                dumpster=TemplateSourceDTO(inline=output_hole_dumpster_inline)
            )
            if output_hole_dumpster_inline is not None
            else None
        ),
    )
    result = await get_notifications_sdk().create_template(request)
    data = result.model_dump(mode="json")
    log.info("create_template_handler")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created template: {data['name']}")
