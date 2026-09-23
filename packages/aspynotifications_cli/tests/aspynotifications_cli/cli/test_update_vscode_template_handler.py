from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from aspynotifications_cli.cli import update_vscode_template_handler as handler_module
from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.notifications_dtos import TemplateDTO, VSCodeTemplateDTO


@pytest.mark.asyncio
async def test_handler_builds_a_vscode_template_update_request(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sdk = SimpleNamespace(
        update_template=AsyncMock(
            return_value=TemplateDTO(
                name="entity-vscode-template",
                vscode=VSCodeTemplateDTO(
                    title=TemplateSourceDTO(inline="Entity created"),
                    message=TemplateSourceDTO(inline="Entity entity-001"),
                    severity="info",
                ),
            )
        )
    )
    monkeypatch.setattr(handler_module, "load_aspynotifications_cli_config", lambda: None)
    monkeypatch.setattr(handler_module, "configure_logging", lambda: None)
    monkeypatch.setattr(handler_module, "get_notifications_sdk", lambda: sdk)

    await handler_module.update_vscode_template_handler(
        name="entity-vscode-template",
        title_inline="Entity created",
        message_inline="Entity entity-001",
        severity="info",
        output_format="json",
    )

    assert '"name": "entity-vscode-template"' in capsys.readouterr().out
    request = sdk.update_template.await_args.args[0]
    assert request.vscode is not None
    assert request.vscode.title.inline == "Entity created"
    assert request.vscode.message.inline == "Entity entity-001"
