#!/usr/bin/env bash
set -eu

notify create-slack-provider \
  --name slack-provider \
  --webhook-url "XXX" \
  --output-format json \
  --config-file /home/zrp0/Workspace/aspynotifications/monoconfig/default/aspynotifications_cli

#notify create-slack-provider --help