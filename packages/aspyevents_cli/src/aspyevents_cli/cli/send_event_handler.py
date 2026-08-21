import json

import structlog
from aspyevents_cli import load_aspyevents_cli_config
from aspyevents_dtos.publish_event_request import PublishEventRequest
from aspyevents_sdk import get_events_sdk
from aspyevents_sdk.aspyevents_sdk import EventsSDK
from aspylogger.services.logging_setup import configure_logging

logger = structlog.get_logger(__name__)


async def send_event_handler(file_path: str, output_format: str) -> None:
    log = logger.bind(function="send_event_handler")

    load_aspyevents_cli_config()
    configure_logging()

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    request = PublishEventRequest.model_validate(data)
    sdk: EventsSDK = get_events_sdk()
    result = await sdk.publish(request)
    log.info("send_event_handler")
    print("Server: ", result)
