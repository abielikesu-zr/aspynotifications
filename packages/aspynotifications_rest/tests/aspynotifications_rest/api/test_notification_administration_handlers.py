from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from aspynotifications_rest.api.notification_administration_handlers import (
    update_template,
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
