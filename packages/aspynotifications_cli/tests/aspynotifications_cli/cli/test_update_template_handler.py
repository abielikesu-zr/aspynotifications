from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from aspynotifications_cli.cli import update_template_handler as handler_module
from aspynotifications_dtos.notifications_dtos import TemplateDTO


@pytest.mark.asyncio
async def test_update_template_handler_builds_a_slack_request(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sdk = SimpleNamespace(
        update_template=AsyncMock(
            return_value=TemplateDTO.model_validate(
                {
                    "name": "slack-template",
                    "slack": {"blocks": {"inline": "blocks: []"}},
                }
            )
        )
    )
    monkeypatch.setattr(handler_module, "load_aspynotifications_cli_config", lambda: None)
    monkeypatch.setattr(handler_module, "configure_logging", lambda: None)
    monkeypatch.setattr(handler_module, "get_notifications_sdk", lambda: sdk)

    await handler_module.update_template_handler(
        name="slack-template",
        slack_blocks_inline="blocks: []",
        output_format="json",
    )

    assert '"name": "slack-template"' in capsys.readouterr().out
    request = sdk.update_template.await_args.args[0]
    assert request.slack is not None
    assert request.slack.blocks is not None
    assert request.slack.blocks.inline == "blocks: []"
