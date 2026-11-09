#!/bin/sh
set -eu

pip install --extra-index-url https://repo.ascloud.io/aspy/prod/simple/  aspynotifications_cli

notifications-worker bootstrap --app-id aspynotifications_worker

rm -rf bootstrap