#!/bin/sh
set -eu
/opt/apps/aspynotifications_worker/.venv/bin/notifications-worker bootstrap   --app-id notification_config
