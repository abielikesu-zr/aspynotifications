from pathlib import Path

import pytest

from aspynotifications.adapters.destinations_file_adapter import DestinationsStoreAdapter
from aspynotifications.services.destinations_service import DestinationsService


def _service(tmp_path: Path) -> DestinationsService:
    store = DestinationsStoreAdapter({"data_dir": str(tmp_path)})
    return DestinationsService(config={}, store=store)


@pytest.mark.asyncio
async def test_localfs_create_retrieve_list_update_and_delete(tmp_path: Path) -> None:
    # Arrange
    service = _service(tmp_path)

    # Act
    first = await service.create_destination(
        name="email-alerts",
        provider="email",
        destination_type="email",
        template="incident-template",
        routable=False,
        config={"type": "email", "to": ["alerts@example.com"]},
    )
    second = await service.create_destination(
        name="slack-alerts",
        provider="slack",
        destination_type="slack_channel",
        template="incident-template",
        routable=False,
        config={"type": "slack_channel", "channel_id": "C123"},
    )

    # Assert
    assert await service.get_destination_by_id(first.id) == first
    assert await service.get_destination_by_name(second.name) == second
    assert {destination.id for destination in await service.list_destinations()} == {
        first.id,
        second.id,
    }

    updated_first = first.model_copy(update={"template": "updated-template"})
    assert await service.update_destination(updated_first) == updated_first
    assert await service.get_destination_by_id(first.id) == updated_first

    await service.delete_destination(second.id)
    assert await service.get_destination_by_id(second.id) is None


@pytest.mark.asyncio
async def test_localfs_persists_all_endpoint_configuration_variants(
    tmp_path: Path,
) -> None:
    # Arrange
    service = _service(tmp_path)

    # Act
    email = await service.create_destination(
        name="email-alerts",
        provider="email",
        destination_type="email",
        template="incident-template",
        routable=False,
        config={"type": "email", "to": ["alerts@example.com"]},
    )
    slack = await service.create_destination(
        name="slack-alerts",
        provider="slack",
        destination_type="slack_channel",
        template="incident-template",
        routable=False,
        config={"type": "slack_channel", "channel_id": "C123"},
    )
    teams = await service.create_destination(
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
    for destination in (email, slack, teams):
        loaded = await service.get_destination_by_id(destination.id)
        assert loaded is not None
        assert loaded.config.type == destination.type


@pytest.mark.asyncio
async def test_localfs_ping_uses_temporary_storage_directory(tmp_path: Path) -> None:
    # Arrange
    service = _service(tmp_path)

    # Act
    result = await service.ping()

    # Assert
    assert result is True
