#!/usr/bin/env bash

set -euo pipefail

if ! command -v notify >/dev/null 2>&1; then
  echo "The 'notify' command is not installed. Run the package generation and installation flow first."
  exit 1
fi

run_id="$(date +%s)"
provider_name="cli-shole-provider-${run_id}"
template_name="cli-output-hole-template-${run_id}"
destination_name="cli-output-hole-destination-${run_id}"
policy_name="cli-policy-${run_id}"

notify create-provider \
  --name "${provider_name}" \
  --type SHOLE \
  --output-format json

notify create-template \
  --name "${template_name}" \
  --output-hole-dumpster-inline "CLI administration command test ${run_id}" \
  --output-format json

notify create-output-hole-destination \
  --name "${destination_name}" \
  --provider "${provider_name}" \
  --template "${template_name}" \
  --routable \
  --output-format json

notify create-policy \
  --name "${policy_name}" \
  --subject "cli.administration.test" \
  --destination "${destination_name}" \
  --output-format json
