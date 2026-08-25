from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from aspynotifications_cli.cli import update_shole_provider_handler as shole_handler
from aspynotifications_cli.cli import update_slack_provider_handler as slack_handler
from aspynotifications_cli.cli import update_zeptomail_provider_handler as zeptomail_handler
from aspynotifications_dtos.providers_dtos import NotificationProviderDTO


def _provider_response(provider: object) -> NotificationProviderDTO:
    return NotificationProviderDTO.model_validate(
        {
            "id": "provider-001",
            "name": "provider-name",
            "provider": provider,
        }
    )


@pytest.mark.asyncio
async def test_update_slack_provider_handler_builds_a_slack_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk = SimpleNamespace(
        update_notification_provider=AsyncMock(
            return_value=_provider_response(
                {
                    "type": "SLACK",
                    "config": {"webhook_url": "https://hooks.slack.com/services/new"},
                }
            )
        )
    )
    monkeypatch.setattr(slack_handler, "load_aspynotifications_cli_config", lambda: None)
    monkeypatch.setattr(slack_handler, "configure_logging", lambda: None)
    monkeypatch.setattr(slack_handler, "get_notifications_sdk", lambda: sdk)

    await slack_handler.update_slack_provider_handler(
        provider_id="provider-001",
        webhook_url="https://hooks.slack.com/services/new",
        output_format="json",
    )

    request = sdk.update_notification_provider.await_args.args[0]
    assert request.provider.type == "SLACK"


@pytest.mark.asyncio
async def test_update_zeptomail_provider_handler_builds_a_zeptomail_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk = SimpleNamespace(
        update_notification_provider=AsyncMock(
            return_value=_provider_response(
                {
                    "type": "ZEPTOMAIL",
                    "config": {
                        "from_address": "notifications@example.com",
                        "from_name": "Notifications",
                        "credentials": {"send_mail_token": "token"},
                    },
                }
            )
        )
    )
    monkeypatch.setattr(zeptomail_handler, "load_aspynotifications_cli_config", lambda: None)
    monkeypatch.setattr(zeptomail_handler, "configure_logging", lambda: None)
    monkeypatch.setattr(zeptomail_handler, "get_notifications_sdk", lambda: sdk)

    await zeptomail_handler.update_zeptomail_provider_handler(
        provider_id="provider-001",
        from_address="notifications@example.com",
        from_name="Notifications",
        send_mail_token="token",
        output_format="json",
    )

    request = sdk.update_notification_provider.await_args.args[0]
    assert request.provider.type == "ZEPTOMAIL"


@pytest.mark.asyncio
async def test_update_shole_provider_handler_builds_a_shole_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sdk = SimpleNamespace(
        update_notification_provider=AsyncMock(
            return_value=_provider_response(
                {
                    "type": "SHOLE",
                    "config": {"level": "INFO", "cows": False},
                }
            )
        )
    )
    monkeypatch.setattr(shole_handler, "load_aspynotifications_cli_config", lambda: None)
    monkeypatch.setattr(shole_handler, "configure_logging", lambda: None)
    monkeypatch.setattr(shole_handler, "get_notifications_sdk", lambda: sdk)

    await shole_handler.update_shole_provider_handler(
        provider_id="provider-001",
        level="INFO",
        cows=False,
        output_format="json",
    )

    request = sdk.update_notification_provider.await_args.args[0]
    assert request.provider.type == "SHOLE"
