import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import ActivateNotificationPolicyRequest
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def activate_notification_policy_handler(
    policy_id: str,
    output_format: str,
) -> None:
    log = logger.bind(function="activate_notification_policy_handler")

    load_aspynotifications_cli_config()
    configure_logging()
    result = await get_notifications_sdk().activate_notification_policy(
        ActivateNotificationPolicyRequest(policy_id=policy_id)
    )
    data = result.model_dump(mode="json")
    log.info("activate_notification_policy_handler", policy_id=policy_id)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Activated notification policy: {data['name']} ({data['id']})")
