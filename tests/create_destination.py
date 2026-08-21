"""Temporary runner for creating a destination through DestinationsService."""

import argparse
import asyncio
import json
from pathlib import Path

from aspyconfig import get_config
from aspyconfig.utils.os_utils import get_os_username
from aspynotifications.config.app_config import AspyEventsAppConfig
from aspynotifications.config.destination_config import DestinationConfig
from aspynotifications.entities.destination import Destination
from aspynotifications.factories.destinations_store_factory import (
    create_destinations_store,
)
from aspynotifications.services.destinations_service import DestinationsService
from pydantic import TypeAdapter

PACKAGE_NAME = "aspynotifications"


def parse_arguments() -> argparse.Namespace:
    """Parse the destination and configuration arguments."""

    parser = argparse.ArgumentParser(
        description="Create a destination using DestinationsService."
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Optional additional configuration directory.",
    )
    parser.add_argument("--name", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument(
        "--type",
        required=True,
        choices=("email", "slack_channel", "teams_conversation"),
    )
    parser.add_argument("--template", required=True)
    parser.add_argument("--routable", action="store_true")
    parser.add_argument(
        "--destination-config",
        required=True,
        help="JSON for Destination.config, according to the selected --type.",
    )
    return parser.parse_args()


def load_app_config(config_dir: Path | None) -> AspyEventsAppConfig:
    """Load default, local, and optional application configuration."""

    config = get_config()
    user_config_paths = [f"monoconfig/default/{PACKAGE_NAME}"]
    if config_dir is not None:
        user_config_paths.append(str(config_dir))

    local_config_paths = []
    local_config_name = get_os_username()
    if local_config_name:
        local_config_paths.append(f"monoconfig/{local_config_name}/{PACKAGE_NAME}")

    config.register_common_config(
        cli_config=None,
        user_config_paths=user_config_paths,
        app_defaults=None,
        local_config_paths=local_config_paths,
    )
    config.load()
    return config.to_pydantic(AspyEventsAppConfig)


def load_destination_config(arguments: argparse.Namespace) -> DestinationConfig:
    """Load and validate the endpoint configuration."""

    destination_config = json.loads(arguments.destination_config)
    destination_config.setdefault("type", arguments.type)
    return TypeAdapter(DestinationConfig).validate_python(destination_config)


async def create_destination(arguments: argparse.Namespace) -> Destination:
    """Create and persist a destination through the domain service."""

    app_config = load_app_config(arguments.config_dir)
    store = create_destinations_store(
        app_config.aspynotifications.destinations_store.model_dump()
    )
    service = DestinationsService(
        config=app_config.aspynotifications.destinations_service.model_dump(),
        store=store,
    )
    return await service.create_destination(
        name=arguments.name,
        provider=arguments.provider,
        template=arguments.template,
        routable=arguments.routable,
        config=load_destination_config(arguments),
    )


def main() -> None:
    """Run the temporary destination creation flow."""

    arguments = parse_arguments()
    destination = asyncio.run(create_destination(arguments))
    print(destination.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
