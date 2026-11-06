import json

import structlog
import yaml
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import CreateTemplateRequest
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def create_template_handler(
    file_path: str,
    output_format: str,
    config_files: list[str] | None = None,
) -> None:
    log = logger.bind(function="create_template_handler")

    load_aspynotifications_cli_config(config_files=config_files)
    configure_logging()

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    request = CreateTemplateRequest.model_validate(data)
    result = await get_notifications_sdk().create_template(request)
    data = result.model_dump(mode="json")
    log.info("create_template_handler")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created template: {data['name']}")
