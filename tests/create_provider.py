"""Temporary runner for creating a provider through ProvidersService."""

import argparse
import asyncio
import json
from pathlib import Path

from aspyconfig import get_config
from aspyconfig.utils.os_utils import get_os_username
from aspynotifications.config.app_config import AspyEventsAppConfig
from aspynotifications.entities.provider import Provider
from aspynotifications.factories.providers_store_factory import create_providers_store
from aspynotifications.services.providers_service import ProvidersService

PACKAGE_NAME = "aspynotifications"


def parse_arguments() -> argparse.Namespace:
    """Parse the provider and configuration arguments."""

    parser = argparse.ArgumentParser(
        description="Create a provider using ProvidersService."
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=None,
        help="Optional additional configuration directory.",
    )
    parser.add_argument("--name", required=True)
    parser.add_argument("--type", required=True, choices=("email", "slack", "teams"))
    parser.add_argument(
        "--provider-config",
        required=True,
        help="JSON for Provider.config, according to the selected --type.",
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


def load_provider_config(arguments: argparse.Namespace) -> dict:
    """Load the integration configuration and supply its discriminator."""

    provider_config = json.loads(arguments.provider_config)
    provider_config.setdefault("type", arguments.type)
    return provider_config


async def create_provider(arguments: argparse.Namespace) -> Provider:
    """Create and persist a provider through the domain service."""

    app_config = load_app_config(arguments.config_dir)
    store = create_providers_store(
        app_config.aspynotifications.providers_store.model_dump()
    )
    service = ProvidersService(store=store)
    return await service.create_provider(
        name=arguments.name,
        provider_type=arguments.type,
        config=load_provider_config(arguments),
    )


def main() -> None:
    """Run the temporary provider creation flow."""

    arguments = parse_arguments()
    provider = asyncio.run(create_provider(arguments))
    print(provider.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
