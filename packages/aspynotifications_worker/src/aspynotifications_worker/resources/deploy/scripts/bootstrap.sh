#!/bin/sh
set -eu

export NOTIFICATIONS_CONFIG_PATH="$PWD/config"

pip install --extra-index-url https://repo.ascloud.io/aspy/prod/simple/  aspynotifications_cli

chmod u+x bootstrap/001-init/apply.sh
sed -i 's/\r$//' bootstrap/001-init/apply.sh

notifications-worker bootstrap --app-id aspynotifications_worker

rm -rf bootstrap