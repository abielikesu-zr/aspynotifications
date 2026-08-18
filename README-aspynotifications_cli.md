# aspynotifications_cli

`aspynotifications_cli` is the command-line client for submitting notification requests to the Notifications REST service through `aspynotifications_sdk`.

## Available command

The package exposes one Click command:

```text
send-event --from-file PATH [--output-format print|json] [-v|-q] [--log-format plain|json]
```

It reads a JSON file, validates it as `CreateNotifyRequest`, loads the SDK configuration, obtains the configured `NotificationsSDK`, and calls `notify`.

Run the command module directly after installing the package:

```bash
python -m aspynotifications_cli.cli.main send-event --from-file notification.json
```

The current handler always prints the server response. `--output-format` is accepted by the command but is not yet used to alter that output.

## Request file

The input must have the `CreateNotifyRequest` shape: a top-level `event` containing a CloudEvents 1.0 envelope. For example:

```json
{
  "event": {
    "type": "incident.created",
    "source": "example-service",
    "subject": "incident-123",
    "data": {
      "event": {
        "title": "Example incident"
      }
    }
  }
}
```

`CloudEventDTO` defaults `specversion` to `1.0`, `time` to the current UTC timestamp, `datacontenttype` to `application/json`, and `data` to an empty event-data object when those fields are omitted.

## Configuration

Before sending, the command loads configuration from:

1. `monoconfig/default/aspynotifications_cli`
2. `monoconfig/<os-user>/aspynotifications_cli`

The default configuration supplies the SDK HTTP-client settings and the REST base URL:

```yaml
notifications_sdk:
  http_client:
    timeout: 5.0
    max_retries: 2
    backoff_base: 0.15
    backoff_max: 1.0
    verify: true
  notifications_client:
    base_url: "http://127.0.0.1:50000"
```

Use the user-specific monoconfig directory to override the REST endpoint or HTTP settings without changing defaults.

## Dependencies and boundaries

The CLI owns argument parsing, logging setup, JSON-file input, and DTO validation. Transport is delegated to `aspynotifications_sdk`; it does not call the REST endpoint directly.

## Installation

```bash
make install PACKAGE_NAME=aspynotifications_cli EDITABLE=true
```

or:

```bash
aspymgr pkg install aspynotifications_cli -e
```

## Tests

The package currently contains no automated test files. Its expected tests should isolate the handler, mock the SDK, verify invalid JSON and invalid DTO input, and verify that configuration is loaded before the SDK is obtained.
