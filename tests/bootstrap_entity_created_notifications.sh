#!/usr/bin/env bash

notify create-slack-provider \
  --name slack-provider \
  --webhook-url "XXX" \
  --output-format json

# --- 

notify create-template \
  --name entity-created-slack-template \
  --slack-blocks-inline "$(cat /Users/zeroramp/Documents/zeroramp/Workspace/aspynotifications/var/notification-templates/entity.created-slack.yaml)" \
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

notify create-policy --name entity-updated-notification-policy --subject "*.updated" --destination entity-slack-destination --output-format json
notify create-policy --name entity-deleted-notification-policy  --subject "*.deleted"  --destination entity-slack-destination --output-format json
notify create-policy --name entity-started-notification-policy --subject "*.started"  --destination entity-slack-destination --output-format json
notify create-policy --name entity-completed-notification-policy --subject "*.completed" --destination entity-slack-destination --output-format json
notify create-policy --name entity-failed-notification-policy --subject "*.failed" --destination entity-slack-destination --output-format json
notify create-policy --name entity-feedback-positive-notification-policy --subject "*.feedback_positive" --destination entity-slack-destination --output-format json
notify create-policy --name entity-feedback-negative-notification-policy --subject "*.feedback_negative" --destination entity-slack-destination --output-format json
notify create-policy --name entity-from-cache-notification-policy --subject "*.from_cache" --destination entity-slack-destination --output-format json
notify create-policy --name entity-regenerated-notification-policy --subject "*.regenerated" --destination entity-slack-destination --output-format json
notify create-policy --name entity-cached-notification-policy --subject "*.cached" --destination entity-slack-destination --output-format json
notify create-policy --name entity-cache-invalidated-notification-policy --subject "*.cache_invalidated" --destination entity-slack-destination --output-format json
notify create-policy --name entity-generated-notification-policy --subject "*.generated" --destination entity-slack-destination --output-format json
notify create-policy --name entity-activated-notification-policy --subject "*.activated" --destination entity-slack-destination --output-format json
notify create-policy --name entity-accepted-notification-policy --subject "*.accepted" --destination entity-slack-destination --output-format json

# --- 

notify create-template \
  --name bot-installed-slack-template \
  --slack-blocks-inline "$(cat /Users/zeroramp/Documents/zeroramp/Workspace/aspynotifications/var/notification-templates/bot.installed-slack.yaml)" \
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
