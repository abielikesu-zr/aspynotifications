from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from aspynotifications_rest.api.notification_administration_handlers import (
    update_template,
    update_notification_provider,
)
from aspynotifications_dtos.providers_dtos import (
    NotificationProviderDTO,
    SlackProviderDTO,
    SlackProviderSettingsDTO,
    UpdateNotificationProviderRequest,
)
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    SlackTemplateDTO,
    TemplateDTO,
    UpdateTemplateRequest,
)


@pytest.mark.asyncio
async def test_update_template_calls_the_facade_and_returns_the_template() -> None:
    body = UpdateTemplateRequest(
        name="slack-template",
        slack=SlackTemplateDTO(blocks=TemplateSourceDTO(inline="blocks: []")),
    )
    facade = SimpleNamespace(
        update_template=AsyncMock(return_value=TemplateDTO.model_validate(body.model_dump()))
    )
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(notifications_facade=facade))
    )

    response = await update_template("slack-template", body, request)

    assert response.status_code == 200
    facade.update_template.assert_awaited_once_with(body)


@pytest.mark.asyncio
async def test_update_provider_calls_the_facade_and_returns_the_provider() -> None:
    body = UpdateNotificationProviderRequest(
        id="provider-001",
        provider=SlackProviderDTO(
            config=SlackProviderSettingsDTO(
                webhook_url="https://hooks.slack.com/services/new"
            )
        ),
    )
    facade = SimpleNamespace(
        update_notification_provider=AsyncMock(
            return_value=NotificationProviderDTO(
                id=body.id,
                name="operations-slack",
                provider=body.provider,
            )
        )
    )
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(notifications_facade=facade))
    )

    response = await update_notification_provider("provider-001", body, request)

    assert response.status_code == 200
    facade.update_notification_provider.assert_awaited_once_with(body)
