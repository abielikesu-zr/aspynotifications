from pydantic import TypeAdapter

from aspynotifications_dtos.notifications_dtos import (
    DestinationConfigDTO,
    VSCodeAllAudienceDTO,
    VSCodeDestinationConfigDTO,
    VSCodeGroupAudienceDTO,
    VSCodeUserAudienceDTO,
)
from aspynotifications_dtos.providers_dtos import (
    NotificationProviderConfigDTO,
    VSCodeProviderDTO,
)


def test_vscode_provider_contract_resolves_discriminator() -> None:
    provider = TypeAdapter(NotificationProviderConfigDTO).validate_python(
        {"type": "VSCODE", "config": {"relay_url": "https://relay.example.test"}}
    )

    assert isinstance(provider, VSCodeProviderDTO)


def test_vscode_destination_contract_supports_each_audience_variant() -> None:
    audiences = [
        {"type": "user", "recipient_user_id": "user@example.com"},
        {"type": "group", "group_id": "operations"},
        {"type": "all"},
    ]

    destinations = [
        TypeAdapter(DestinationConfigDTO).validate_python(
            {"type": "vscode", "audience": audience}
        )
        for audience in audiences
    ]

    assert all(isinstance(destination, VSCodeDestinationConfigDTO) for destination in destinations)
    assert isinstance(destinations[0].audience, VSCodeUserAudienceDTO)
    assert isinstance(destinations[1].audience, VSCodeGroupAudienceDTO)
    assert isinstance(destinations[2].audience, VSCodeAllAudienceDTO)
