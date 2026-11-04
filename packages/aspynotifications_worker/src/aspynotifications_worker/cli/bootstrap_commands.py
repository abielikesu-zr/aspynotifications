"""Execute bootstrap operations using the worker's configuration sources."""

import click
from aspyconfig import get_config as aspy_get_config
from aspyconfig.utils.os_utils import get_os_username
from aspypatch.cli.apply_patches_handler import run_apply_patches

PACKAGE_NAME = "aspynotifications_worker"


async def run_bootstrap(
    app_id: str,
    patch_version: str | None,
    force: bool,
    config_files: list[str] | None = None,
) -> None:
    """Register worker config, delegate patch execution, and present the result."""
    user_config_paths = [f"monoconfig/default/{PACKAGE_NAME}"]
    local_config_paths: list[str] = list()
    username = get_os_username()
    if username:
        local_config_paths.append(f"monoconfig/{username}/{PACKAGE_NAME}")

    config = aspy_get_config()
    config.register_common_config(
        cli_config=None,
        user_config_paths=user_config_paths,
        local_config_paths=local_config_paths,
    )

    response = await run_apply_patches(
        app_id=app_id,
        patch_version=patch_version,
        force=force,
        config_files=config_files,
    )

    for result in response.results:
        click.echo(f"{result.patch_version}: {result.outcome.value}")

    if not response.success:
        raise click.ClickException("Bootstrap patch execution failed.")
