from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    UpdateNotificationPolicyByNameRequest,
    SlackTemplateDTO,
    UpdateTemplateRequest,
)
from aspynotifications_dtos.providers_dtos import (
    SlackProviderDTO,
    SlackProviderSettingsDTO,
    UpdateNotificationProviderRequest,
)
from aspynotifications_sdk.adapters.notifications_rest_client import (
    NotificationsRestClient,
)


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def json(self) -> dict:
        return self._payload


@pytest.mark.asyncio
async def test_update_policy_by_name_uses_put_with_the_policy_name() -> None:
    request = UpdateNotificationPolicyByNameRequest(
        name="entity-created-notification-policy",
        subject="*.created",
        destinations=["entity-vscode-destination"],
    )
    http_client = MagicMock()
    http_client.put = AsyncMock(
        return_value=_Response(
            {
                "id": "policy-001",
                "name": request.name,
                "subject": request.subject,
                "destinations": request.destinations,
                "envelope_policies": [],
                "destination_policies": [],
                "is_active": True,
            }
        )
    )
    client = NotificationsRestClient(
        config={"base_url": "http://notifications.example"},
        http_client=http_client,
    )

    result = await client.update_notification_policy_by_name(request)

    assert result.name == request.name
    http_client.put.assert_awaited_once_with(
        "http://notifications.example/api/v1/policies/by-name/entity-created-notification-policy",
        payload=request.model_dump(mode="json"),
    )


@pytest.mark.asyncio
async def test_update_template_uses_put_with_the_template_name() -> None:
    request = UpdateTemplateRequest(
        name="slack-template",
        slack=SlackTemplateDTO(blocks=TemplateSourceDTO(inline="blocks: []")),
    )
    http_client = MagicMock()
    http_client.put = AsyncMock(return_value=_Response(request.model_dump(mode="json")))
    client = NotificationsRestClient(
        config={"base_url": "http://notifications.example"},
        http_client=http_client,
    )

    result = await client.update_template(request)

    assert result.name == request.name
    http_client.put.assert_awaited_once_with(
        "http://notifications.example/api/v1/templates/slack-template",
        payload=request.model_dump(mode="json"),
    )


@pytest.mark.asyncio
async def test_update_provider_uses_put_with_the_provider_id() -> None:
    request = UpdateNotificationProviderRequest(
        id="provider-001",
        provider=SlackProviderDTO(
            config=SlackProviderSettingsDTO(
                webhook_url="https://hooks.slack.com/services/new"
            )
        ),
    )
    http_client = MagicMock()
    http_client.put = AsyncMock(
        return_value=_Response(
            {
                "id": request.id,
                "name": "operations-slack",
                "provider": request.provider.model_dump(),
            }
        )
    )
    client = NotificationsRestClient(
        config={"base_url": "http://notifications.example"},
        http_client=http_client,
    )

    result = await client.update_notification_provider(request)

    assert result.id == request.id
    http_client.put.assert_awaited_once_with(
        "http://notifications.example/api/v1/providers/provider-001",
        payload=request.model_dump(mode="json"),
    )
