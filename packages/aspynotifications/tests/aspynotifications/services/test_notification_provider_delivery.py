from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications.adapters.notification_senders.slack_sender import (
    SlackNotificationSender,
)
from aspynotifications.adapters.notification_senders.zeptomail_sender import (
    ZeptoMailNotificationSender,
)
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)


class StubSenderFactory:
    def __init__(self, sender: object) -> None:
        self._sender = sender

    def create(self, provider_type: str) -> object:
        return self._sender


def _service(sender_factory: object | None = None) -> NotificationProviderService:
    store = MagicMock(spec=NotificationProviderStore)
    store.ping = AsyncMock(return_value=True)
    return NotificationProviderService(
        notification_provider_store=store,
        config={},
        sender_factory=sender_factory,
    )


def _provider(provider_type: str) -> NotificationProvider:
    config_by_type = {
        "SLACK": {"webhook_url": "https://hooks.slack.com/services/example"},
        "ZEPTOMAIL": {
            "from_address": "notifications@example.com",
            "credentials": {"send_mail_token": "token"},
        },
    }
    return NotificationProvider.model_validate(
        {
            "id": "provider-001",
            "name": "provider-under-test",
            "provider": {"type": provider_type, "config": config_by_type[provider_type]},
        }
    )


def _destination(destination_type: str) -> Destination:
    config_by_type = {
        "email": {"type": "email", "to": ["alerts@example.com"]},
        "slack_channel": {"type": "slack_channel", "channel_id": "C123"},
    }
    return Destination.model_validate(
        {
            "id": "destination-001",
            "name": "destination-under-test",
            "provider": "provider-under-test",
            "type": destination_type,
            "template": "template-under-test",
            "config": config_by_type[destination_type],
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("provider_type", "destination_type", "sender_class"),
    [
        ("SLACK", "slack_channel", SlackNotificationSender),
        ("ZEPTOMAIL", "email", ZeptoMailNotificationSender),
    ],
)
async def test_send_uses_the_sender_selected_by_provider_type(
    provider_type: str,
    destination_type: str,
    sender_class: type,
    capsys: pytest.CaptureFixture[str],
) -> None:
    http_client = MagicMock()
    http_client.post = AsyncMock(return_value=MagicMock(status_code=201))

    result = await _service(StubSenderFactory(sender_class(http_client))).send(
        provider=_provider(provider_type),
        destination=_destination(destination_type),
        message={"subject": "test", "html": "<p>test</p>", "body": "test"},
    )

    assert result.status == "simulated"
    assert result.sender_name == sender_class.__name__
    assert result.provider_type == provider_type
    assert "provider-under-test" in capsys.readouterr().out
