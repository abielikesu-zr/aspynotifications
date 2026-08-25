from unittest.mock import AsyncMock, MagicMock

import pytest
from aspypolicies.services.policy_service import PolicyService

from aspynotifications.entities.notification_policy import NotificationPolicy
from aspynotifications.ports.policies_store import NotificationPolicyStore
from aspynotifications.services.policy_service import NotificationPolicyService
from aspynotifications.services.subject_trie import SubjectTrie


def _policy(is_active: bool = True) -> NotificationPolicy:
    return NotificationPolicy(
        id="policy-001",
        name="tenant-created",
        subject="tenant.created",
        envelope_policies=[],
        destination_policies=[],
        destinations=["tenant-destination"],
        is_active=is_active,
    )


def _store(policy: NotificationPolicy | None) -> MagicMock:
    store = MagicMock(spec=NotificationPolicyStore)
    store.get_notification_policy_by_id = AsyncMock(return_value=policy)
    store.get_notification_policy_by_name = AsyncMock(return_value=policy)
    store.list_notification_policies = AsyncMock(return_value=[] if policy is None else [policy])
    store.save_notification_policy = AsyncMock()
    store.delete_notification_policy = AsyncMock()
    store.ping = AsyncMock(return_value=True)
    return store


def _service(store: MagicMock) -> NotificationPolicyService:
    return NotificationPolicyService(
        notification_policy_store=store,
        config={},
        policy_service=MagicMock(spec=PolicyService),
        context_transformer=MagicMock(),
        subject_trie=SubjectTrie(),
    )


def test_notification_policy_is_active_by_default() -> None:
    policy = NotificationPolicy(
        id="policy-001",
        name="tenant-created",
        subject="tenant.created",
        envelope_policies=[],
        destination_policies=[],
        destinations=["tenant-destination"],
    )

    assert policy.is_active is True


@pytest.mark.asyncio
async def test_deactivate_notification_policy_persists_inactive_state() -> None:
    policy = _policy()
    store = _store(policy)

    result = await _service(store).deactivate_notification_policy(policy.id)

    assert result.is_active is False
    store.save_notification_policy.assert_awaited_once_with(policy)


@pytest.mark.asyncio
async def test_activate_notification_policy_persists_active_state() -> None:
    policy = _policy(is_active=False)
    store = _store(policy)

    result = await _service(store).activate_notification_policy(policy.id)

    assert result.is_active is True
    store.save_notification_policy.assert_awaited_once_with(policy)


@pytest.mark.asyncio
async def test_inactive_policy_is_excluded_from_subscriptions() -> None:
    policy = _policy(is_active=False)
    store = _store(policy)

    subscriptions = await _service(store).get_subscriptions()

    assert subscriptions == []
