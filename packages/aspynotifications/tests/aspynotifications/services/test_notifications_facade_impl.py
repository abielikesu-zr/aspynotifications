from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications.services.notifications_facade_impl import (
    NotificationsFacadeImpl,
)
from aspynotifications_dtos.notify_request import CreateNotifyRequest


def _request() -> CreateNotifyRequest:
    return CreateNotifyRequest.model_validate(
        {
            "event": {
                "id": "event-001",
                "source": "infra-service",
                "type": "infrastructure.node.error",
                "subject": "node.123",
                "data": {"context": {"environment": "production"}},
            }
        }
    )


def _facade() -> tuple[
    NotificationsFacadeImpl,
    MagicMock,
    MagicMock,
    MagicMock,
    AsyncMock,
]:
    cloud_event_service = MagicMock()
    cloud_event_service.create_cloud_event = AsyncMock()

    destination_one = SimpleNamespace(
        name="operations-email",
        provider="mail-provider",
        template="email-template",
    )
    destination_two = SimpleNamespace(
        name="operations-slack",
        provider="slack-provider",
        template="slack-template",
    )
    destinations_service = MagicMock()
    destinations_service.get_destination_by_name = AsyncMock(
        side_effect=[destination_one, destination_two]
    )

    template_service = MagicMock()
    template_service.get_template_by_name = AsyncMock(
        side_effect=[SimpleNamespace(name="email-template"), SimpleNamespace(name="slack-template")]
    )

    notification_provider_service = MagicMock()
    notification_provider_service.get_notification_provider_by_name = AsyncMock(
        side_effect=[SimpleNamespace(name="mail-provider"), SimpleNamespace(name="slack-provider")]
    )
    notification_provider_service.send = AsyncMock()

    notification_policy_service = MagicMock()
    notification_policy_service.event_to_context.return_value = {
        "envelope": {"type": "infrastructure.node.error"}
    }
    find_matching_policies = AsyncMock(
        return_value=[
            SimpleNamespace(destinations=["operations-email", "operations-slack"]),
            SimpleNamespace(destinations=["operations-slack"]),
        ]
    )
    notification_policy_service.find_matching_policies = find_matching_policies

    notification_template_renderer = MagicMock()
    notification_template_renderer.render.side_effect = [
        {"subject": "email"},
        {"blocks": []},
    ]

    facade = NotificationsFacadeImpl(
        cloud_event_service=cloud_event_service,
        template_service=template_service,
        destinations_service=destinations_service,
        notification_provider_service=notification_provider_service,
        notification_policy_service=notification_policy_service,
        notification_template_renderer=notification_template_renderer,
        config={"keep": "keep"},
    )
    return (
        facade,
        cloud_event_service,
        notification_provider_service,
        destinations_service,
        find_matching_policies,
    )


@pytest.mark.asyncio
async def test_notify_persists_event_and_delivers_once_per_destination() -> None:
    (
        facade,
        cloud_event_service,
        notification_provider_service,
        destinations_service,
        find_matching_policies,
    ) = _facade()

    result = await facade.notify(_request())

    assert result == "ok"
    cloud_event_service.create_cloud_event.assert_awaited_once()
    assert destinations_service.get_destination_by_name.await_count == 2
    assert notification_provider_service.send.await_count == 2

    await_args = find_matching_policies.await_args
    assert await_args is not None
    event = await_args.args[0]
    assert "event" not in event["data"]
    assert "error" not in event["data"]
    assert "routing" not in event["data"]


@pytest.mark.asyncio
async def test_notify_propagates_a_delivery_failure() -> None:
    facade, _, notification_provider_service, destinations_service, _ = _facade()
    notification_provider_service.send.side_effect = RuntimeError("delivery failed")

    with pytest.raises(RuntimeError, match="delivery failed"):
        await facade.notify(_request())

    assert destinations_service.get_destination_by_name.await_count == 1
    assert notification_provider_service.send.await_count == 1
