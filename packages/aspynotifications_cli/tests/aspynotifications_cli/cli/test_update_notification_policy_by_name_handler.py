from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from aspynotifications_cli.cli import update_notification_policy_by_name_handler as handler_module
from aspynotifications_dtos.notifications_dtos import NotificationPolicyDTO


@pytest.mark.asyncio
async def test_handler_builds_a_request_identified_by_name(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sdk = SimpleNamespace(
        update_notification_policy_by_name=AsyncMock(
            return_value=NotificationPolicyDTO(
                id="policy-001",
                name="entity-created-notification-policy",
                subject="*.created",
                destinations=["entity-vscode-destination"],
                envelope_policies=[],
                destination_policies=[],
                is_active=True,
            )
        )
    )
    monkeypatch.setattr(handler_module, "load_aspynotifications_cli_config", lambda: None)
    monkeypatch.setattr(handler_module, "configure_logging", lambda: None)
    monkeypatch.setattr(handler_module, "get_notifications_sdk", lambda: sdk)

    await handler_module.update_notification_policy_by_name_handler(
        name="entity-created-notification-policy",
        subject="*.created",
        destinations=("entity-vscode-destination",),
        envelope_policy=(),
        negative_envelope_policy=(),
        destination_policy=(),
        negative_destination_policy=(),
        output_format="json",
    )

    assert '"name": "entity-created-notification-policy"' in capsys.readouterr().out
    request = sdk.update_notification_policy_by_name.await_args.args[0]
    assert request.name == "entity-created-notification-policy"
    assert request.destinations == ["entity-vscode-destination"]
