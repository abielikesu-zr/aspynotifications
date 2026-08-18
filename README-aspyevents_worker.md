# aspyevents_worker

`aspyevents_worker` is the reusable NATS JetStream worker foundation for CloudEvents in this repository. It supplies the connection lifecycle, stream and consumer management, configuration loading, tracing, retry behaviour, and a Click command factory. Application packages implement the event-specific worker by subclassing `CloudEventsWorker`.

## Responsibilities

| Component | Responsibility |
| --- | --- |
| `CloudEventsWorker` | Abstract worker that creates or validates a JetStream stream, creates pull consumers, deserializes `CloudEventDTO` messages, invokes `handle`, and acknowledges or negatively acknowledges messages. |
| `BaseWorkerRunner` | Loads NATS configuration, establishes and drains the NATS connection, installs shutdown handlers, and owns the worker task lifecycle. |
| `worker_start_command` | Produces the shared `worker start` Click command for a concrete runner and worker factory. |
| `CloudEventsWorkerConfig` | Defines worker name, stream, subscriptions, batch size, acknowledgement wait time, and delivery limit. |
| `NatsConnectionConfig` | Defines NATS URL, optional credentials, and optional TLS files. |

## Processing flow

1. The runner loads configuration and validates the NATS connection settings.
2. It connects to NATS and obtains a JetStream context.
3. The worker verifies that the configured stream exists with the expected subject, or creates it.
4. It creates a durable pull consumer for every configured subscription.
5. Each message is validated as `CloudEventDTO`, then handled inside a consumer tracing span.
6. A successful handler result acknowledges the message; a failure logs the exception and sends a negative acknowledgement with a one-second delay.

`CloudEventsWorker` is abstract: an application must implement `handle(self, cloud_event)` before it can process events. It can also override `get_subscriptions()` when subscriptions come from application state instead of static configuration.

## Configuration

`BaseWorkerRunner.load_config()` merges, in order, built-in NATS defaults, `monoconfig/default/<package>`, an optional file passed through `--configfile`, and `monoconfig/<os-user>/<package>`.

The runner subclass defines the configuration root. A concrete worker therefore needs both a NATS connection and worker configuration at its selected root, for example:

```yaml
my_worker:
  nats_connection:
    nats_url: "nats://localhost:4222"
  nats_worker:
    name: "my-worker"
    subscriptions:
      - "my.events"
```

The stream defaults to `EVENTS` and `events.>`. Subscriptions not already beginning with the stream prefix are prefixed automatically.

## Command integration

Applications create a Click command by calling `worker_start_command(runner=..., worker_factory=...)`. The resulting command accepts:

```text
worker start [--configfile PATH] [--nats-url URL] [-v|-q] [--log-format console|json]
```

The runner requires configuration to be loaded before `run()`; the generated command does this automatically.

## Installation

From the repository root:

```bash
make install PACKAGE_NAME=aspyevents_worker EDITABLE=true
```

or:

```bash
aspymgr pkg install aspyevents_worker -e
```

## Tests

The package currently contains no automated test files. A useful test suite should cover stream creation and mismatch detection, subscription normalization, successful acknowledgement, negative acknowledgement after a handler failure, and graceful shutdown of the NATS connection.
