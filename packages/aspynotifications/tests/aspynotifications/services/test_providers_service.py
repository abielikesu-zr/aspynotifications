import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from aspynotifications.entities.notification_provider import (
    GmailProviderConfig,
    SlackProviderConfig,
    ZeptoMailProviderConfig,
)
from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)


def _gmail_config() -> dict:
    return {
        "from_address": "notifications@example.com",
        "from_name": "Notifications",
        "credentials": {
            "service_account_email": "service@example.com",
            "private_key": "private-key",
            "delegated_user": "notifications@example.com",
        },
    }


def _store() -> MagicMock:
    store = MagicMock(spec=NotificationProviderStore)
    store.get_notification_provider_by_id = AsyncMock(return_value=None)
    store.get_notification_provider_by_name = AsyncMock(return_value=None)
    store.list_notification_providers = AsyncMock(return_value=[])
    store.save_notification_provider = AsyncMock()
    store.delete_notification_provider = AsyncMock()
    store.ping = AsyncMock(return_value=True)
    return store


@pytest.mark.asyncio
async def test_create_provider_generates_uuid_and_persists_gmail_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    store = _store()
    provider_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setattr(
        "aspynotifications.services.notification_provider_service.uuid4",
        lambda: provider_id,
    )

    # Act
    provider = await NotificationProviderService(
        notification_provider_store=store,
        config={},
    ).create_notification_provider(
        name="corporate-mail",
        provider_type="GMAIL",
        config=_gmail_config(),
    )

    # Assert
    assert provider.id == str(provider_id)
    assert isinstance(provider.provider, GmailProviderConfig)
    store.save_notification_provider.assert_called_once_with(provider)


@pytest.mark.asyncio
async def test_create_provider_resolves_slack_and_zeptomail_config_variants() -> None:
    # Arrange
    store = _store()
    service = NotificationProviderService(
        notification_provider_store=store,
        config={},
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
    assert isinstance(slack.provider, SlackProviderConfig)
    assert isinstance(zeptomail.provider, ZeptoMailProviderConfig)


@pytest.mark.asyncio
async def test_create_provider_rejects_invalid_config() -> None:
    # Arrange
    store = _store()

    # Act / Assert
    with pytest.raises(ValidationError):
        await NotificationProviderService(
            notification_provider_store=store,
            config={},
        ).create_notification_provider(
            name="corporate-mail",
            provider_type="GMAIL",
            config={"from_address": "notifications@example.com"},
        )

    store.save_notification_provider.assert_not_called()
