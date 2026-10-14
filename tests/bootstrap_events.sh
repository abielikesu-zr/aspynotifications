#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

usage() {
  echo "Usage: $(basename "$0") <environment-config.yaml>" >&2
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command not found: $1" >&2
    exit 1
  }
}

[[ $# -eq 1 ]] || { usage; exit 1; }
readonly CONFIG_FILE="$1"
[[ -f "$CONFIG_FILE" ]] || { echo "Configuration file not found: $CONFIG_FILE" >&2; exit 1; }

require_command notify
require_command yq
require_command jq

readonly CONFIG_JSON="$(yq --output-format=json '.' "$CONFIG_FILE")"

jq --exit-status '
  .commands | type == "array" and length > 0 and
  all(.[]; ((.action | type) == "string" and (.action | length) > 0) and ((.options | type) == "object"))
' <<<"$CONFIG_JSON" >/dev/null || {
  echo "Invalid configuration: commands must be a non-empty list with action and options." >&2
  exit 1
}

run_command() {
  local action="$1"
  local options_json="$2"
  local file_options_json="$3"
  local key type value file_path
  local -a command values

  command=(notify "$action")

  while IFS=$'\t' read -r key type value; do
    if [[ "$type" == "array" ]]; then
      mapfile -t values < <(jq -r --arg key "$key" '.[$key][] | tostring' <<<"$options_json")
      command+=("--$key" "${values[@]}")
    else
      command+=("--$key" "$value")
    fi
  done < <(jq -r '
    to_entries[] |
    [.key, (.value | type), (if (.value | type) == "array" then "" else (.value | tostring) end)] |
    @tsv
  ' <<<"$options_json")

  while IFS=$'\t' read -r key file_path; do
    [[ -f "$file_path" ]] || { echo "Referenced template file not found: $file_path" >&2; exit 1; }
    command+=("--$key" "$(<"$file_path")")
  done < <(jq -r 'to_entries[] | [.key, .value] | @tsv' <<<"$file_options_json")

  command+=(--output-format json)
  "${command[@]}"
}

cd "$PROJECT_DIR"

while IFS= read -r command_json; do
  action="$(jq -r '.action' <<<"$command_json")"
  options_json="$(jq -c '.options' <<<"$command_json")"
  file_options_json="$(jq -c '.file_options // {}' <<<"$command_json")"
  run_command "$action" "$options_json" "$file_options_json"
done < <(jq -c '.commands[]' <<<"$CONFIG_JSON")
