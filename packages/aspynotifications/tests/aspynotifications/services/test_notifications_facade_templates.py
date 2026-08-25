from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications.services.notifications_facade_impl import (
    NotificationsFacadeImpl,
)
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    SlackTemplateDTO,
    UpdateTemplateRequest,
)


@pytest.mark.asyncio
async def test_update_template_delegates_to_template_service() -> None:
    template_service = MagicMock()
    template_service.update_template = AsyncMock(
        side_effect=lambda template: template
    )
    facade = NotificationsFacadeImpl(
        template_service=template_service,
        destinations_service=MagicMock(),
        notification_provider_service=MagicMock(),
        notification_policy_service=MagicMock(),
        notification_template_renderer=MagicMock(),
        config={},
    )
    request = UpdateTemplateRequest(
        name="slack-template",
        slack=SlackTemplateDTO(blocks=TemplateSourceDTO(inline="blocks: []")),
    )

    result = await facade.update_template(request)

    assert result.name == request.name
    assert result.slack == request.slack
    template_service.update_template.assert_awaited_once()
