import json

import structlog
from aspyevents_dtos.notify_request import CreateNotifyRequest
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def send_event_handler(file_path: str, output_format: str) -> None:
    log = logger.bind(function="send_event_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    request = CreateNotifyRequest.model_validate(data)
    sdk = get_notifications_sdk()
    result = await sdk.notify(request)
    log.info("send_event_handler")
    print("Server: ", result)
