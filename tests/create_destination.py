"""Temporary runner for creating a destination through DestinationsService."""

import argparse
import asyncio
import json
from pathlib import Path

from aspyconfig import get_config
from aspyconfig.utils.os_utils import get_os_username

from aspynotifications.config.app_config import AspynotificationsAppConfig
from aspynotifications.config.destination_config import (
    EmailDestinationConfig,
    SlackChannelDestinationConfig,
    TeamsConversationDestinationConfig,
)
from aspynotifications.entities.destination import Destination
from aspynotifications.factories.destinations_store_factory import (
    create_destinations_store,
)
from aspynotifications.services.destinations_service import DestinationsService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "aspynotifications"
PLUGINS_CONFIG_DIR = (
    PROJECT_ROOT
    / "packages"
    / "aspynotifications"
    / "src"
    / "aspynotifications"
    / "resources"
    / "config"
)


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
        choices=("email", "channel", "conversation"),
    )
    parser.add_argument("--template", required=True)
    parser.add_argument("--routable", action="store_true")
    parser.add_argument(
        "--destination-config",
        required=True,
        help="JSON for Destination.config, according to the selected --type.",
    )
    return parser.parse_args()


def load_app_config(config_dir: Path | None) -> AspynotificationsAppConfig:
    """Load default, local, optional, and generated plugin configuration."""

    config = get_config()
    user_config_paths = [f"monoconfig/default/{PACKAGE_NAME}"]
    if config_dir is not None:
        user_config_paths.append(str(config_dir))
    user_config_paths.append(str(PLUGINS_CONFIG_DIR))

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
    return config.to_pydantic(AspynotificationsAppConfig)


def build_destination_config(destination_type: str, raw_config: str):
    """Validate the type-specific destination configuration."""

    config_data = json.loads(raw_config)
    config_by_type = {
        "email": EmailDestinationConfig,
        "channel": SlackChannelDestinationConfig,
        "conversation": TeamsConversationDestinationConfig,
    }
    return config_by_type[destination_type].model_validate(config_data)


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
        destination_type=arguments.type,
        template=arguments.template,
        routable=arguments.routable,
        config=build_destination_config(
            arguments.type,
            arguments.destination_config,
        ),
    )


def main() -> None:
    """Run the temporary destination creation flow."""

    arguments = parse_arguments()
    destination = asyncio.run(create_destination(arguments))
    print(destination.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
