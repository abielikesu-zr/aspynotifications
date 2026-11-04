"""Configure the shared aspypatch command for the notifications worker."""

import asyncio
from pathlib import Path

import click
import structlog
from aspylogger.services.logging_setup import bootstrap_logging
from aspynotifications_worker.cli.bootstrap_commands import run_bootstrap
from aspypatch.cli.apply_patches_cmd import apply_patches

logger = structlog.get_logger(__name__)

PACKAGE_NAME = "aspynotifications_worker"


def _run_bootstrap(
    app_id: str,
    patch_version: str | None,
    force: bool,
    verbose: int,
    quiet: int,
    log_format: str | None,
    log_file: Path | None,
    config_file: tuple[Path, ...] | None,
) -> None:
    """Initialize CLI logging and delegate bootstrap execution."""
    root_packages = [PACKAGE_NAME, "aspypatch"]
    log_Filestr = str(log_file) if log_file else None
    bootstrap_logging(
        verbose=verbose,
        quiet=quiet,
        log_format=log_format,
        root_package=root_packages,
        log_file=log_Filestr,
    )

    try:
        config_files = [str(path) for path in config_file] if config_file else None
        asyncio.run(
            run_bootstrap(
                app_id=app_id,
                patch_version=patch_version,
                force=force,
                config_files=config_files,
            )
        )

    except click.ClickException:
        raise
    except Exception as exc:
        logger.error(
            "bootstrap_failed",
            app_id=app_id,
            patch_version=patch_version,
            error=str(exc),
            exc_info=exc,
        )
        raise click.ClickException(f"Failed to bootstrap notifications: {exc}") from exc


def bootstrap_command() -> click.Command:
    """Reuse aspypatch options with the worker's logging and config initialization."""
    return click.Command(
        name="bootstrap",
        callback=_run_bootstrap,
        params=apply_patches.params,
        help="Apply bootstrap patches using the notifications worker configuration.",
    )
