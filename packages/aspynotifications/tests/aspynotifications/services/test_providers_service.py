import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from aspynotifications.entities.notification_provider import (
    NotificationProvider,
    SlackProvider,
    ZeptoMailProvider,
)
from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)


def _store() -> MagicMock:
    store = MagicMock(spec=NotificationProviderStore)
    store.get_notification_provider_by_id = AsyncMock(return_value=None)
    store.get_notification_provider_by_name = AsyncMock(return_value=None)
    store.list_notification_providers = AsyncMock(return_value=[])
    store.save_notification_provider = AsyncMock()
    store.delete_notification_provider = AsyncMock()
    store.ping = AsyncMock(return_value=True)
    return store


def _sender_factory() -> MagicMock:
    return MagicMock()


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_create_provider_resolves_slack_and_zeptomail_config_variants() -> None:
    # Arrange
    store = _store()
    service = NotificationProviderService(
        notification_provider_store=store,
        config={},
        sender_factory=_sender_factory(),
    )

    # Act
    slack = await service.create_notification_provider(
        name="slack-production",
        provider_type="SLACK",
        config={"webhook_url": "https://hooks.slack.com/services/example"},
    )
    zeptomail = await service.create_notification_provider(
        name="zeptomail-production",
        provider_type="ZEPTOMAIL",
        config={
            "from_address": "notifications@example.com",
            "credentials": {"send_mail_token": "zeptomail-token"},
        },
    )

    # Assert
    assert isinstance(slack.provider, SlackProvider)
    assert isinstance(zeptomail.provider, ZeptoMailProvider)


@pytest.mark.asyncio
async def test_create_provider_rejects_invalid_config() -> None:
    # Arrange
    store = _store()

    # Act / Assert
    with pytest.raises(ValidationError):
        await NotificationProviderService(
            notification_provider_store=store,
            config={},
            sender_factory=_sender_factory(),
        ).create_notification_provider(
            name="slack-production",
            provider_type="SLACK",
            config={},
        )

    store.save_notification_provider.assert_not_called()


@pytest.mark.asyncio
async def test_update_provider_preserves_identity_and_replaces_slack_config() -> None:
    store = _store()
    existing = NotificationProvider.model_validate(
        {
            "id": "provider-001",
            "name": "operations-slack",
            "provider": {
                "type": "SLACK",
                "config": {"webhook_url": "https://hooks.slack.com/services/old"},
            },
        }
    )
    store.get_notification_provider_by_id.return_value = existing
    service = NotificationProviderService(
        notification_provider_store=store,
        config={},
        sender_factory=_sender_factory(),
    )

    updated = await service.update_notification_provider(
        provider_id=existing.id,
        provider_type="SLACK",
        config={"webhook_url": "https://hooks.slack.com/services/new"},
    )

    assert updated.id == existing.id
    assert updated.name == existing.name
    assert isinstance(updated.provider, SlackProvider)
    assert updated.provider.config.webhook_url.endswith("/new")
    store.save_notification_provider.assert_awaited_once_with(updated)
