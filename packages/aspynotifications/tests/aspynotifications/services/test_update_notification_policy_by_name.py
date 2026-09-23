from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications.entities.notification_policy import NotificationPolicy
from aspynotifications.services.notifications_facade_impl import (
    NotificationsFacadeImpl,
)
from aspynotifications_dtos.notifications_dtos import (
    UpdateNotificationPolicyByNameRequest,
)


def _facade(policy_service: MagicMock) -> NotificationsFacadeImpl:
    return NotificationsFacadeImpl(
        template_service=MagicMock(),
        destinations_service=MagicMock(),
        notification_provider_service=MagicMock(),
        notification_policy_service=policy_service,
        notification_template_renderer=MagicMock(),
        config={},
    )


def _policy() -> NotificationPolicy:
    return NotificationPolicy(
        id="policy-001",
        name="entity-created-notification-policy",
        subject="*.created",
        destinations=["entity-slack-destination"],
    )


@pytest.mark.asyncio
async def test_update_policy_by_name_resolves_the_policy_then_updates_it() -> None:
    # Arrange
    existing_policy = _policy()
    updated_policy = existing_policy.model_copy(
        update={"destinations": ["entity-vscode-destination"]}
    )
    policy_service = MagicMock()
    policy_service.get_notification_policy_by_name = AsyncMock(
        return_value=existing_policy
    )
    policy_service.update_notification_policy = AsyncMock(return_value=updated_policy)
    request = UpdateNotificationPolicyByNameRequest(
        name=existing_policy.name,
        subject=existing_policy.subject,
        destinations=["entity-vscode-destination"],
    )

    # Act
    result = await _facade(policy_service).update_notification_policy_by_name(request)

    # Assert
    assert result.destinations == ["entity-vscode-destination"]
    policy_service.get_notification_policy_by_name.assert_awaited_once_with(
        existing_policy.name
    )
    policy_service.update_notification_policy.assert_awaited_once_with(
        policy_id=existing_policy.id,
        subject=existing_policy.subject,
        envelope_policies=[],
        destination_policies=[],
        destinations=["entity-vscode-destination"],
    )


@pytest.mark.asyncio
async def test_update_policy_by_name_raises_when_the_policy_does_not_exist() -> None:
    # Arrange
    policy_service = MagicMock()
    policy_service.get_notification_policy_by_name = AsyncMock(return_value=None)
    request = UpdateNotificationPolicyByNameRequest(
        name="missing-policy",
        subject="*.created",
        destinations=["entity-vscode-destination"],
    )

    # Act / Assert
    with pytest.raises(LookupError, match="Notification policy not found: missing-policy"):
        await _facade(policy_service).update_notification_policy_by_name(request)

    policy_service.get_notification_policy_by_name.assert_awaited_once_with(
        "missing-policy"
    )
