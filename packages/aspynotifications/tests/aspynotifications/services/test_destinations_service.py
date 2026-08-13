import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from aspynotifications.config.destination_config import (
    EmailDestinationConfig,
    SlackChannelDestinationConfig,
    TeamsConversationDestinationConfig,
)
from aspynotifications.entities.destination import Destination
from aspynotifications.ports.destinations_store_port import IDestinationStorePort
from aspynotifications.services.destinations_service import DestinationsService


def _email_config() -> dict:
    return {"type": "email", "to": ["alerts@example.com"], "cc": [], "bcc": []}


def _destination(destination_id: str = "destination-001") -> Destination:
    return Destination(
        id=destination_id,
        name="email-alerts",
        provider="email",
        type="email",
        template="incident-template",
        config=_email_config(),
    )


def _store() -> MagicMock:
    store = MagicMock(spec=IDestinationStorePort)
    store.get_destination = AsyncMock(return_value=None)
    store.get_destination_by_name = AsyncMock(return_value=None)
    store.list_destinations = AsyncMock(return_value=[])
    store.save_destination = AsyncMock()
    store.delete_destination = AsyncMock()
    store.ping = AsyncMock(return_value=True)
    return store


def _service(store: MagicMock) -> DestinationsService:
    return DestinationsService(config={}, store=store)


@pytest.mark.asyncio
async def test_create_destination_generates_uuid_and_persists_email_destination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    store = _store()
    destination_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setattr(
        "aspynotifications.services.destinations_service.uuid.uuid4",
        lambda: destination_id,
    )

    # Act
    destination = await _service(store).create_destination(
        name="email-alerts",
        provider="email",
        destination_type="email",
        template="incident-template",
        routable=False,
        config=_email_config(),
    )

    # Assert
    assert destination.id == str(destination_id)
    assert isinstance(destination.config, EmailDestinationConfig)
    store.get_destination.assert_called_once_with(str(destination_id))
    store.get_destination_by_name.assert_called_once_with("email-alerts")
    store.save_destination.assert_called_once_with(destination)


@pytest.mark.asyncio
async def test_create_destination_resolves_slack_config_variant() -> None:
    # Arrange
    store = _store()

    # Act
    destination = await _service(store).create_destination(
        name="slack-alerts",
        provider="slack",
        destination_type="slack_channel",
        template="incident-template",
        routable=False,
        config={"type": "slack_channel", "channel_id": "C123"},
    )

    # Assert
    assert isinstance(destination.config, SlackChannelDestinationConfig)
    store.save_destination.assert_called_once_with(destination)


@pytest.mark.asyncio
async def test_create_destination_resolves_teams_config_variant() -> None:
    # Arrange
    store = _store()

    # Act
    destination = await _service(store).create_destination(
        name="teams-alerts",
        provider="teams",
        destination_type="teams_conversation",
        template="incident-template",
        routable=False,
        config={
            "type": "teams_conversation",
            "service_url": "https://smba.trafficmanager.net/amer/",
            "conversation_id": "conversation-001",
        },
    )

    # Assert
    assert isinstance(destination.config, TeamsConversationDestinationConfig)
    store.save_destination.assert_called_once_with(destination)


@pytest.mark.asyncio
async def test_create_destination_rejects_unknown_config_discriminator() -> None:
    # Arrange
    store = _store()

    # Act / Assert
    with pytest.raises(ValidationError):
        await _service(store).create_destination(
            name="invalid-destination",
            provider="slack",
            destination_type="slack_channel",
            template="incident-template",
            routable=False,
            config={"type": "unknown"},
        )

    store.save_destination.assert_not_called()


@pytest.mark.asyncio
async def test_create_destination_rejects_incomplete_config() -> None:
    # Arrange
    store = _store()

    # Act / Assert
    with pytest.raises(ValidationError):
        await _service(store).create_destination(
            name="invalid-destination",
            provider="slack",
            destination_type="slack_channel",
            template="incident-template",
            routable=False,
            config={"type": "slack_channel"},
        )

    store.save_destination.assert_not_called()


@pytest.mark.asyncio
async def test_create_destination_rejects_duplicate_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    store = _store()
    destination_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    store.get_destination = AsyncMock(return_value=_destination("duplicate-id"))
    monkeypatch.setattr(
        "aspynotifications.services.destinations_service.uuid.uuid4",
        lambda: destination_id,
    )

    # Act / Assert
    with pytest.raises(ValueError, match="Destination ID already exists"):
        await _service(store).create_destination(
            name="email-alerts",
            provider="email",
            destination_type="email",
            template="incident-template",
            routable=False,
            config=_email_config(),
        )

    store.get_destination.assert_called_once_with(str(destination_id))
    store.save_destination.assert_not_called()


@pytest.mark.asyncio
async def test_create_destination_rejects_duplicate_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    store = _store()
    destination_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
    store.get_destination_by_name = AsyncMock(return_value=_destination())
    monkeypatch.setattr(
        "aspynotifications.services.destinations_service.uuid.uuid4",
        lambda: destination_id,
    )

    # Act / Assert
    with pytest.raises(ValueError, match="Destination name already exists"):
        await _service(store).create_destination(
            name="email-alerts",
            provider="email",
            destination_type="email",
            template="incident-template",
            routable=False,
            config=_email_config(),
        )

    store.get_destination.assert_called_once_with(str(destination_id))
    store.get_destination_by_name.assert_called_once_with("email-alerts")
    store.save_destination.assert_not_called()


@pytest.mark.asyncio
async def test_get_destination_by_id_returns_store_result() -> None:
    # Arrange
    store = _store()
    destination = _destination()
    store.get_destination = AsyncMock(return_value=destination)
    service = _service(store)

    # Act
    result = await service.get_destination_by_id(destination.id)

    # Assert
    assert result is destination
    store.get_destination.assert_called_once_with(destination.id)


@pytest.mark.asyncio
async def test_get_destination_by_name_returns_store_result() -> None:
    # Arrange
    store = _store()
    destination = _destination()
    store.get_destination_by_name = AsyncMock(return_value=destination)
    service = _service(store)

    # Act
    result = await service.get_destination_by_name(destination.name)

    # Assert
    assert result is destination
    store.get_destination_by_name.assert_called_once_with(destination.name)


@pytest.mark.asyncio
async def test_list_destinations_returns_store_result() -> None:
    # Arrange
    store = _store()
    destination = _destination()
    store.list_destinations = AsyncMock(return_value=[destination])
    service = _service(store)

    # Act
    result = await service.list_destinations()

    # Assert
    assert result == [destination]
    store.list_destinations.assert_called_once_with()


@pytest.mark.asyncio
async def test_update_destination_persists_existing_destination() -> None:
    # Arrange
    store = _store()
    destination = _destination()
    store.get_destination = AsyncMock(return_value=destination)
    store.get_destination_by_name = AsyncMock(return_value=destination)

    # Act
    updated = await _service(store).update_destination(destination)

    # Assert
    assert updated is destination
    store.get_destination.assert_called_once_with(destination.id)
    store.get_destination_by_name.assert_called_once_with(destination.name)
    store.save_destination.assert_called_once_with(destination)


@pytest.mark.asyncio
async def test_update_destination_rejects_missing_destination() -> None:
    # Arrange
    store = _store()
    destination = _destination()

    # Act / Assert
    with pytest.raises(ValueError, match="Destination not found"):
        await _service(store).update_destination(destination)

    store.get_destination.assert_called_once_with(destination.id)
    store.save_destination.assert_not_called()


@pytest.mark.asyncio
async def test_update_destination_rejects_duplicate_name() -> None:
    # Arrange
    store = _store()
    destination = _destination()
    store.get_destination = AsyncMock(return_value=destination)
    store.get_destination_by_name = AsyncMock(return_value=_destination("other-id"))

    # Act / Assert
    with pytest.raises(ValueError, match="Destination name already exists"):
        await _service(store).update_destination(destination)

    store.get_destination.assert_called_once_with(destination.id)
    store.get_destination_by_name.assert_called_once_with(destination.name)
    store.save_destination.assert_not_called()


@pytest.mark.asyncio
async def test_delete_destination_delegates_to_store() -> None:
    # Arrange
    store = _store()
    destination = _destination()
    store.get_destination = AsyncMock(return_value=destination)
    service = _service(store)

    # Act
    await service.delete_destination(destination.id)

    # Assert
    store.get_destination.assert_called_once_with(destination.id)
    store.delete_destination.assert_called_once_with(destination.id)


@pytest.mark.asyncio
async def test_delete_destination_rejects_missing_destination() -> None:
    # Arrange
    store = _store()

    # Act / Assert
    with pytest.raises(ValueError, match="Destination not found"):
        await _service(store).delete_destination("missing-id")

    store.get_destination.assert_called_once_with("missing-id")
    store.delete_destination.assert_not_called()


@pytest.mark.asyncio
async def test_ping_returns_store_result() -> None:
    # Arrange
    store = _store()
    service = _service(store)

    # Act
    result = await service.ping()

    # Assert
    assert result is True
    store.ping.assert_called_once_with()
