#!/usr/bin/env bash

set -euo pipefail

if ! command -v notify >/dev/null 2>&1; then
  echo "The 'notify' command is not installed. Run the package generation and installation flow first."
  exit 1
fi

run_id="$(date +%s)-$$"
slack_provider_name="cli-slack-provider-${run_id}"
zeptomail_provider_name="cli-zeptomail-provider-${run_id}"
shole_provider_name="cli-shole-provider-${run_id}"
email_template_name="cli-email-template-${run_id}"
slack_template_name="cli-slack-template-${run_id}"
output_hole_template_name="cli-output-hole-template-${run_id}"
email_destination_name="cli-email-destination-${run_id}"
slack_destination_name="cli-slack-destination-${run_id}"
output_hole_destination_name="cli-output-hole-destination-${run_id}"
policy_name="cli-policy-${run_id}"

notify create-slack-provider \
  --name "${slack_provider_name}" \
  --webhook-url "https://example.invalid/slack-${run_id}" \
  --output-format json

notify create-zeptomail-provider \
  --name "${zeptomail_provider_name}" \
  --from-address "cli-${run_id}@example.invalid" \
  --from-name "CLI Administration Test" \
  --send-mail-token "cli-zeptomail-token-${run_id}" \
  --output-format json

notify create-shole-provider \
  --name "${shole_provider_name}" \
  --level WARN \
  --cows \
  --output-format json

notify create-template \
  --name "${email_template_name}" \
  --email-subject-inline "CLI email template ${run_id}" \
  --email-html-inline "<p>CLI email template ${run_id}</p>" \
  --email-text-inline "CLI email template ${run_id}" \
  --output-format json

notify create-template \
  --name "${slack_template_name}" \
  --slack-blocks-inline "blocks: []" \
  --output-format json

notify create-template \
  --name "${output_hole_template_name}" \
  --output-hole-dumpster-inline "CLI administration command test ${run_id}" \
  --output-format json

notify create-email-destination \
  --name "${email_destination_name}" \
  --provider "${zeptomail_provider_name}" \
  --template "${email_template_name}" \
  --to "alerts-${run_id}@example.invalid" \
  --cc "audit-${run_id}@example.invalid" \
  --bcc "archive-${run_id}@example.invalid" \
  --routable \
  --output-format json

notify create-slack-channel-destination \
  --name "${slack_destination_name}" \
  --provider "${slack_provider_name}" \
  --template "${slack_template_name}" \
  --channel-id "C${run_id//-/}" \
  --routable \
  --output-format json

notify create-output-hole-destination \
  --name "${output_hole_destination_name}" \
  --provider "${shole_provider_name}" \
  --template "${output_hole_template_name}" \
  --routable \
  --output-format json

notify create-policy \
  --name "${policy_name}" \
  --subject "cli.administration.test" \
  --destination "${email_destination_name}" \
  --destination "${slack_destination_name}" \
  --destination "${output_hole_destination_name}" \
  --envelope-policy "cli-envelope-policy" "envelope.source == 'cli-test'" "CLI envelope policy" \
  --negative-envelope-policy "cli-negative-envelope-policy" "envelope.type == 'ignored'" "CLI negative envelope policy" \
  --destination-policy "cli-destination-policy" "destination.routable == true" "CLI destination policy" \
  --negative-destination-policy "cli-negative-destination-policy" "destination.name == 'ignored'" "CLI negative destination policy" \
  --output-format json
