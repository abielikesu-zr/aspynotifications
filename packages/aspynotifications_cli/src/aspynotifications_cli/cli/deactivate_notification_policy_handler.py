import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import DeactivateNotificationPolicyRequest
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


async def deactivate_notification_policy_handler(
    policy_id: str,
    output_format: str,
) -> None:
    log = logger.bind(function="deactivate_notification_policy_handler")

    load_aspynotifications_cli_config()
    configure_logging()
    result = await get_notifications_sdk().deactivate_notification_policy(
        DeactivateNotificationPolicyRequest(policy_id=policy_id)
    )
    data = result.model_dump(mode="json")
    log.info("deactivate_notification_policy_handler", policy_id=policy_id)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Deactivated notification policy: {data['name']} ({data['id']})")
