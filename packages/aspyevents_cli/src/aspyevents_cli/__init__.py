from aspyconfig import get_config as aspy_get_config
from aspyconfig.utils.os_utils import get_os_username

PACKAGE_NAME = __package__ or ""


def load_aspyevents_cli_config(
    config_file: str | None = None,
) -> None:
    package_name = (PACKAGE_NAME or "").split(".")[0]
    user_config_paths = [f"monoconfig/default/{package_name}"]
    if config_file:
        user_config_paths.append(config_file)

    local_config_paths = []
    local_config_name = get_os_username()
    if local_config_name:
        local_config_paths.append(f"monoconfig/{local_config_name}/{package_name}")

    config = aspy_get_config()
    config.register_common_config(
        cli_config=None,
        app_defaults=None,
        user_config_paths=user_config_paths,
        local_config_paths=local_config_paths,
    )
    config.load()
