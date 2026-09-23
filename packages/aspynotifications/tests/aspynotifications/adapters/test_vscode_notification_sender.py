from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications.adapters.notification_senders.vscode_sender import (
    VSCodeNotificationSender,
)
from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.adapters.notify_renderer_vscode import VSCodeNotificationRenderer
from aspynotifications.config.destination_config import VSCodeDestinationConfig
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.entities.source import TemplateSource
from aspynotifications.entities.template import Template, VSCodeTemplate


def _provider() -> NotificationProvider:
    return NotificationProvider.model_validate(
        {
            "id": "provider-001",
            "name": "vscode-relay",
            "provider": {
                "type": "VSCODE",
                "config": {"relay_url": "https://relay.example.test/notifications"},
            },
        }
    )


def _destination(audience: dict[str, str]) -> Destination:
    return Destination.model_validate(
        {
            "id": "destination-001",
            "name": "vscode-destination",
            "provider": "vscode-relay",
            "type": "vscode",
            "template": "vscode-template",
            "config": {"type": "vscode", "audience": audience},
        }
    )


@pytest.mark.asyncio
async def test_sender_posts_rendered_message_and_user_audience() -> None:
    # Arrange
    http_client = MagicMock()
    http_client.post = AsyncMock(return_value=MagicMock(status_code=202))
    sender = VSCodeNotificationSender(http_client=http_client)
    destination = _destination({"type": "user", "recipient_user_id": "user@example.com"})

    # Act
    result = await sender.send(
        provider=_provider(),
        destination=destination,
        message={"title": "Completed", "message": "The ingestion completed", "severity": "info"},
    )

    # Assert
    assert result.status == "accepted"
    assert result.provider_type == "VSCODE"
    http_client.post.assert_awaited_once_with(
        "https://relay.example.test/notifications",
        headers={"Content-Type": "application/json"},
        payload={
            "title": "Completed",
            "message": "The ingestion completed",
            "severity": "info",
            "audience": {"type": "user", "recipient_user_id": "user@example.com"},
            "recipient_user_id": "user@example.com",
        },
    )


@pytest.mark.parametrize(
    "audience",
    [
        {"type": "group", "group_id": "operations"},
        {"type": "all"},
    ],
)
@pytest.mark.asyncio
async def test_sender_preserves_future_audience_variants(audience: dict[str, str]) -> None:
    # Arrange
    http_client = MagicMock()
    http_client.post = AsyncMock(return_value=MagicMock(status_code=202))
    sender = VSCodeNotificationSender(http_client=http_client)

    # Act
    await sender.send(
        provider=_provider(),
        destination=_destination(audience),
        message={"title": "Title", "message": "Message", "severity": "warning"},
    )

    # Assert
    payload = http_client.post.await_args.kwargs["payload"]
    assert payload["audience"] == audience


def test_renderer_renders_vscode_template() -> None:
    # Arrange
    jinja_renderer = MagicMock(spec=Jinja2TemplateRenderer)
    jinja_renderer.render_inline.side_effect = ["Completed", "Ingestion 42 completed"]
    renderer = VSCodeNotificationRenderer(renderer=jinja_renderer)
    template = Template(
        name="vscode-template",
        vscode=VSCodeTemplate(
            title=TemplateSource(inline="{{ context.title }}"),
            message=TemplateSource(inline="{{ context.message }}"),
            severity="info",
        ),
    )

    # Act
    result = renderer.render(template=template, context={"context": {}})

    # Assert
    assert result == {
        "title": "Completed",
        "message": "Ingestion 42 completed",
        "severity": "info",
    }
