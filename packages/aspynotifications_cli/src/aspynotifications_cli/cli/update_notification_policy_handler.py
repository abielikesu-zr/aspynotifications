import json

import structlog
from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import (
    PolicyExpressionDTO,
    UpdateNotificationPolicyRequest,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config

logger = structlog.get_logger(__name__)


def _policy_expressions(
    values: tuple[tuple[str, str, str], ...],
    negative: bool,
) -> list[PolicyExpressionDTO]:
    return [
        PolicyExpressionDTO(
            name=name,
            expression=expression,
            reason=reason,
            negative=negative,
        )
        for name, expression, reason in values
    ]


async def update_notification_policy_handler(
    policy_id: str,
    subject: str,
    destinations: tuple[str, ...],
    envelope_policy: tuple[tuple[str, str, str], ...],
    negative_envelope_policy: tuple[tuple[str, str, str], ...],
    destination_policy: tuple[tuple[str, str, str], ...],
    negative_destination_policy: tuple[tuple[str, str, str], ...],
    output_format: str,
) -> None:
    log = logger.bind(function="update_notification_policy_handler")

    load_aspynotifications_cli_config()
    configure_logging()

    request = UpdateNotificationPolicyRequest(
        id=policy_id,
        subject=subject,
        destinations=list(destinations),
        envelope_policies=(
            _policy_expressions(envelope_policy, negative=False)
            + _policy_expressions(negative_envelope_policy, negative=True)
        ),
        destination_policies=(
            _policy_expressions(destination_policy, negative=False)
            + _policy_expressions(negative_destination_policy, negative=True)
        ),
    )
    result = await get_notifications_sdk().update_notification_policy(request)
    data = result.model_dump(mode="json")
    log.info("update_notification_policy_handler", policy_id=policy_id)
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Updated notification policy: {data['name']} ({data['id']})")
