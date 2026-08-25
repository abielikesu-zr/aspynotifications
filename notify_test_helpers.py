from typing import Any

from pydantic import TypeAdapter

from aspynotifications.config.destination_config import (
    DestinationConfig,
    DestinationType,
)
from aspynotifications.entities.template import Template
from aspynotifications.services.destinations_service import DestinationsService
from aspynotifications.services.template_service import TemplateService


async def ensure_policy(
    service,
    *,
    name: str,
    subject: str,
    envelope_policies: list,
    destination_policies: list,
    destinations: list[str],
):
    existing = await service.get_notification_policy_by_name(name)
    if existing:
        print(f"Policy already exists: {name}")
        return existing

    policy = await service.create_notification_policy(
        name=name,
        subject=subject,
        envelope_policies=envelope_policies,
        destination_policies=destination_policies,
        destinations=destinations,
    )
    print(f"Policy created: {name}")
    return policy


async def ensure_destination(
    service,
    *,
    name: str,
    provider: str,
    destination_type: DestinationType,
    template: str,
    config: dict[str, Any],
):
    existing = await service.get_destination_by_name(name)

    if existing:
        print(f"Destination already exists: {name}")
        return existing

    destination_config_data = dict(config)
    destination_config_data.setdefault("type", destination_type)
    destination_config = TypeAdapter(DestinationConfig).validate_python(
        destination_config_data
    )

    destination = await service.create_destination(
        name=name,
        provider=provider,
        template=template,
        config=destination_config,
    )

    print(f"Destination created: {name}")
    return destination


async def ensure_template(
    service: TemplateService,
    *,
    name: str,
    template: Template,
) -> Template:
    existing = await service.get_template_by_name(name)

    if existing:
        print(f"Template already exists: {name}")
        return existing

    created = await service.create_template(template)

    print(f"Template created: {name}")
    return created


async def get_policy_destinations(
    destinations_service: DestinationsService,
    policy,
):
    destinations = []

    for destination_name in policy.destinations:
        destination = await destinations_service.get_destination_by_name(
            destination_name
        )

        if destination is not None:
            destinations.append(destination)

    return destinations


async def ensure_notification_provider(
    service,
    *,
    name: str,
    provider_type: str,
    config: dict[str, Any],
):
    existing = await service.get_notification_provider_by_name(name)

    if existing:
        print(f"Provider already exists: {name}")
        return existing

    provider = await service.create_notification_provider(
        name=name,
        provider_type=provider_type,
        config=config,
    )

    print(f"Provider created: {name}")
    return provider
