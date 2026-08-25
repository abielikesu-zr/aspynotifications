#!/usr/bin/env bash

notify create-slack-provider \
  --name slack-provider \
  --webhook-url "XXX" \
  --output-format json

notify create-template \
  --name entity-created-slack-template \
  --slack-blocks-inline "$(cat /Volumes/DDEXT/Zeroramp/ws/Workspace/aspynotifications/var/notification-templates/entity.created-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name entity-slack-destination \
  --provider slack-provider \
  --template entity-created-slack-template \
  --output-format json

notify create-policy \
  --name entity-created-notification-policy \
  --subject "*.created" \
  --destination entity-slack-destination \
  --output-format json

notify create-template \
  --name bot-installed-slack-template \
  --slack-blocks-inline "$(cat /Volumes/DDEXT/Zeroramp/ws/Workspace/aspynotifications/var/notification-templates/bot.installed-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name bot-installed-slack-destination \
  --provider slack-provider \
  --template bot-installed-slack-template \
  --output-format json

notify create-policy \
  --name bot-installed-notification-policy \
  --subject "bot.installed" \
  --destination bot-installed-slack-destination \
  --output-format json
