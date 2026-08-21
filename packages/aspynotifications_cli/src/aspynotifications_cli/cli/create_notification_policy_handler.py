import json

from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import (
    CreateNotificationPolicyRequest,
    PolicyExpressionDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config


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


async def create_notification_policy_handler(
    name: str,
    subject: str,
    destinations: tuple[str, ...],
    envelope_policy: tuple[tuple[str, str, str], ...],
    negative_envelope_policy: tuple[tuple[str, str, str], ...],
    destination_policy: tuple[tuple[str, str, str], ...],
    negative_destination_policy: tuple[tuple[str, str, str], ...],
    output_format: str,
) -> None:
    load_aspynotifications_cli_config()
    configure_logging()

    request = CreateNotificationPolicyRequest(
        name=name,
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
    result = await get_notifications_sdk().create_notification_policy(request)
    data = result.model_dump(mode="json")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created notification policy: {data['name']} ({data['id']})")
