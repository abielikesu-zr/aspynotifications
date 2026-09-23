#!/usr/bin/env bash

notify create-vscode-provider \
  --name vscode-provider \
  --relay-url "http://127.0.0.1:8000/notifications" \
  --output-format json

notify create-vscode-template \
  --name entity-vscode-template \
  --title-inline '✨ {{ envelope.type.split(".")[0] | capitalize }} {{ envelope.type.split(".")[1] }}' \
  --message-inline '{% if context.admin_url is defined %}{{ event.name }} · {{ envelope.subject }} · {{ context.admin_url }}{% else %}{{ event.name }} · {{ envelope.subject }}{% endif %}' \
  --severity info \
  --output-format json

notify update-vscode-template \
  --name entity-vscode-template \
  --title-inline '✨ {{ envelope.type.split(".")[0] | capitalize }} {{ envelope.type.split(".")[1] }}' \
  --message-inline '{% if context.admin_url is defined %}{{ event.name }} · {{ envelope.subject }} · {{ context.admin_url }}{% else %}{{ event.name }} · {{ envelope.subject }}{% endif %}' \
  --severity info \
  --output-format json

notify create-vscode-destination \
  --name entity-vscode-destination \
  --provider vscode-provider \
  --template entity-vscode-template \
  --recipient-user-id "afranio.solano@zeroramp.com" \
  --output-format json

notify create-vscode-template --name bot-installed-vscode-template --title-inline '🤖 Bot installed' --message-inline 'Bot: {{ envelope.subject }} · Installation: {{ event.installation_id }} · Platform: {{ event.platform }} · Tenant: {{ context.tenant_id }} · Owner tenant: {{ context.owner_tenant_id }}' --severity info --output-format json
notify create-vscode-destination --name bot-installed-vscode-destination --provider vscode-provider --template bot-installed-vscode-template --recipient-user-id "afranio.solano@zeroramp.com" --output-format json

notify create-vscode-template --name ingestion-started-vscode-template --title-inline '🚀 Ingestion started' --message-inline 'Run: {{ context.run_id }} · Tenant: {{ context.tenant_id }} · Knowledge base: {{ context.kb_id }} · Sources: {{ event.total_kb_sources }}' --severity info --output-format json
notify create-vscode-destination --name ingestion-started-vscode-destination --provider vscode-provider --template ingestion-started-vscode-template --recipient-user-id "afranio.solano@zeroramp.com" --output-format json

notify create-vscode-template --name ingestion-completed-vscode-template --title-inline '✅ Ingestion completed' --message-inline 'Run: {{ context.run_id }} · Tenant: {{ context.tenant_id }} · Knowledge base: {{ context.kb_id }} · Completed at: {{ event.completed_at }}' --severity info --output-format json
notify create-vscode-destination --name ingestion-completed-vscode-destination --provider vscode-provider --template ingestion-completed-vscode-template --recipient-user-id "afranio.solano@zeroramp.com" --output-format json

notify create-vscode-template --name ingestion-failed-vscode-template --title-inline '❌ Ingestion failed' --message-inline 'Run: {{ context.run_id }} · Tenant: {{ context.tenant_id }} · Knowledge base: {{ context.kb_id }} · Failure: {{ event.failure_type }} · Reason: {{ event.reason }}' --severity error --output-format json
notify create-vscode-destination --name ingestion-failed-vscode-destination --provider vscode-provider --template ingestion-failed-vscode-template --recipient-user-id "afranio.solano@zeroramp.com" --output-format json

notify create-vscode-template --name document-changed-vscode-template --title-inline '📄 Document changed' --message-inline 'Document: {{ event.document_name }} · ID: {{ event.document_id }} · Tenant: {{ context.tenant_id }} · Knowledge base: {{ context.kb_id }} · Updated at: {{ event.last_updated_at }}' --severity info --output-format json
notify create-vscode-destination --name document-changed-vscode-destination --provider vscode-provider --template document-changed-vscode-template --recipient-user-id "afranio.solano@zeroramp.com" --output-format json

notify create-vscode-template --name ci-vscode-template --title-inline '🏗️ CI {{ envelope.type }}' --message-inline 'Run: {{ event.run_id }} · Status: {{ event.status }} · Duration: {{ event.duration_seconds }} seconds · Target package: {{ event.target_package }} · Packages rebuilt: {{ event.packages_rebuilt | join(", ") }}' --severity info --output-format json
notify create-vscode-destination --name ci-vscode-destination --provider vscode-provider --template ci-vscode-template --recipient-user-id "afranio.solano@zeroramp.com" --output-format json

notify create-policy --name entity-created-notification-policy --subject "*.created" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-updated-notification-policy --subject "*.updated" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-deleted-notification-policy --subject "*.deleted" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-started-notification-policy --subject "*.started" --destination entity-vscode-destination --negative-envelope-policy "exclude-ingestion-started" "envelope.type == 'ingestion.started'" "Ingestion started has its own Slack destination" --output-format json
notify create-policy --name entity-feedback-positive-notification-policy --subject "*.feedback_positive" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-feedback-negative-notification-policy --subject "*.feedback_negative" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-from-cache-notification-policy --subject "*.from_cache" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-regenerated-notification-policy --subject "*.regenerated" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-cached-notification-policy --subject "*.cached" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-cache-invalidated-notification-policy --subject "*.cache_invalidated" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-generated-notification-policy --subject "*.generated" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-activated-notification-policy --subject "*.activated" --destination entity-vscode-destination --output-format json
notify create-policy --name entity-accepted-notification-policy --subject "*.accepted" --destination entity-vscode-destination --output-format json
notify create-policy --name bot-installed-notification-policy --subject "bot.installed" --destination bot-installed-vscode-destination --output-format json
notify create-policy --name ingestion-started-notification-policy --subject "ingestion.started" --destination ingestion-started-vscode-destination --output-format json
notify create-policy --name ingestion-completed-notification-policy --subject "ingestion.completed" --destination ingestion-completed-vscode-destination --output-format json
notify create-policy --name ingestion-failed-notification-policy --subject "ingestion.failed" --destination ingestion-failed-vscode-destination --output-format json
notify create-policy --name document-changed-notification-policy --subject "document.changed" --destination document-changed-vscode-destination --output-format json
notify create-policy --name ci-notification-policy --subject "ci.>" --destination ci-vscode-destination --output-format json

notify update-policy-by-name --name entity-created-notification-policy --subject "*.created" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-updated-notification-policy --subject "*.updated" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-deleted-notification-policy --subject "*.deleted" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-started-notification-policy --subject "*.started" --destination entity-vscode-destination --negative-envelope-policy "exclude-ingestion-started" "envelope.type == 'ingestion.started'" "Ingestion started has its own Slack destination" --output-format json
notify update-policy-by-name --name entity-feedback-positive-notification-policy --subject "*.feedback_positive" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-feedback-negative-notification-policy --subject "*.feedback_negative" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-from-cache-notification-policy --subject "*.from_cache" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-regenerated-notification-policy --subject "*.regenerated" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-cached-notification-policy --subject "*.cached" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-cache-invalidated-notification-policy --subject "*.cache_invalidated" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-generated-notification-policy --subject "*.generated" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-activated-notification-policy --subject "*.activated" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name entity-accepted-notification-policy --subject "*.accepted" --destination entity-vscode-destination --output-format json
notify update-policy-by-name --name bot-installed-notification-policy --subject "bot.installed" --destination bot-installed-vscode-destination --output-format json
notify update-policy-by-name --name ingestion-started-notification-policy --subject "ingestion.started" --destination ingestion-started-vscode-destination --output-format json
notify update-policy-by-name --name ingestion-completed-notification-policy --subject "ingestion.completed" --destination ingestion-completed-vscode-destination --output-format json
notify update-policy-by-name --name ingestion-failed-notification-policy --subject "ingestion.failed" --destination ingestion-failed-vscode-destination --output-format json
notify update-policy-by-name --name document-changed-notification-policy --subject "document.changed" --destination document-changed-vscode-destination --output-format json
notify update-policy-by-name --name ci-notification-policy --subject "ci.>" --destination ci-vscode-destination --output-format json
