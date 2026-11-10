#!/usr/bin/env bash
set -eu

notify create-slack-provider \
  --from-file 001-slack-provider.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 002-entity-created-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 003-entity-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 004-entity-created-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 005-entity-updated-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 006-entity-deleted-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 007-entity-started-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 008-entity-feedback-positive-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 009-entity-feedback-negative-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 010-entity-from-cache-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 011-entity-regenerated-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 012-entity-cached-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 013-entity-cache-invalidated-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 014-entity-generated-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 015-entity-activated-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 016-entity-accepted-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 017-bot-installed-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 018-bot-installed-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 019-bot-installed-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 020-ingestion-started-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 021-ingestion-started-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 022-ingestion-started-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 023-ingestion-completed-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 024-ingestion-completed-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 025-ingestion-completed-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 026-ingestion-failed-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 027-ingestion-failed-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 028-ingestion-failed-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 029-document-changed-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 030-document-changed-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 031-document-changed-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 032-bot-response-cache-invalidated-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 033-bot-response-cache-invalidated-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 034-bot-response-cache-invalidated-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 035-bot-response-cached-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 036-bot-response-cached-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 037-bot-response-cached-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-template \
  --from-file 038-ci-slack-template.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-slack-channel-destination \
  --from-file 039-ci-slack-destination.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"


notify create-policy \
  --from-file 040-ci-notification-policy.yaml \
  --output-format json \
  --config-file "$NOTIFICATIONS_CONFIG_PATH"

