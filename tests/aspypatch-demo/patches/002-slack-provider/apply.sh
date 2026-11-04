#!/usr/bin/env bash
set -eu

notify create-slack-provider \
  --name slack-provider \
  --webhook-url "XXX" \
  --output-format json \
  --configfile /home/zrp0/Workspace/aspynotifications/monoconfig/default/aspynotifications_cli
