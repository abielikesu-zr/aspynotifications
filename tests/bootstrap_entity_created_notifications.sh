#!/usr/bin/env bash

notify create-slack-provider \
  --name slack-provider \
  --webhook-url "XXX" \
  --output-format json

# --- 

notify create-template \
  --name entity-created-slack-template \
  --slack-blocks-inline "$(cat tests/notification-templates/entity.created-slack.yaml)" \
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
notify create-policy --name entity-started-notification-policy --subject "*.started"  --destination entity-slack-destination --negative-envelope-policy "exclude-ingestion-started" "envelope.type == 'ingestion.started'" "Ingestion started has its own Slack destination" --output-format json
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
  --slack-blocks-inline "$(cat tests/notification-templates/bot.installed-slack.yaml)" \
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

# ---

notify create-template \
  --name ingestion-started-slack-template \
  --slack-blocks-inline "$(cat tests/notification-templates/ingestion.started-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name ingestion-started-slack-destination \
  --provider slack-provider \
  --template ingestion-started-slack-template \
  --output-format json

notify create-policy \
  --name ingestion-started-notification-policy \
  --subject "ingestion.started" \
  --destination ingestion-started-slack-destination \
  --output-format json

# ---

notify create-template \
  --name ingestion-completed-slack-template \
  --slack-blocks-inline "$(cat tests/notification-templates/ingestion.completed-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name ingestion-completed-slack-destination \
  --provider slack-provider \
  --template ingestion-completed-slack-template \
  --output-format json

notify create-policy \
  --name ingestion-completed-notification-policy \
  --subject "ingestion.completed" \
  --destination ingestion-completed-slack-destination \
  --output-format json

# ---

notify create-template \
  --name ingestion-failed-slack-template \
  --slack-blocks-inline "$(cat tests/notification-templates/ingestion.failed-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name ingestion-failed-slack-destination \
  --provider slack-provider \
  --template ingestion-failed-slack-template \
  --output-format json

notify create-policy \
  --name ingestion-failed-notification-policy \
  --subject "ingestion.failed" \
  --destination ingestion-failed-slack-destination \
  --output-format json

# ---

notify create-template \
  --name document-changed-slack-template \
  --slack-blocks-inline "$(cat tests/notification-templates/document.changed-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name document-changed-slack-destination \
  --provider slack-provider \
  --template document-changed-slack-template \
  --output-format json

notify create-policy \
  --name document-changed-notification-policy \
  --subject "document.changed" \
  --destination document-changed-slack-destination \
  --output-format json

# ---

notify create-template \
  --name ci-slack-template \
  --slack-blocks-inline "$(cat tests/notification-templates/ci-slack.yaml)" \
  --output-format json

notify create-slack-channel-destination \
  --name ci-slack-destination \
  --provider slack-provider \
  --template ci-slack-template \
  --output-format json

notify create-policy \
  --name ci-notification-policy \
  --subject "ci.>" \
  --destination ci-slack-destination \
  --output-format json