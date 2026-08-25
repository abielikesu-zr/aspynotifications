from unittest.mock import AsyncMock, MagicMock

import pytest

from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import (
    SlackTemplateDTO,
    UpdateTemplateRequest,
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
