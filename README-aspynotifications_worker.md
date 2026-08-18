# aspynotifications_worker

`aspynotifications_worker` is the application worker that receives CloudEvents from NATS JetStream and delegates notification processing to the `aspynotifications` domain facade. It builds on the generic facilities in `aspyevents_worker`.

## Processing flow

1. `NotificationsWorkerRunner` loads the `aspynotifications_worker.nats_connection` configuration and starts the generic worker runner.
2. The dependency-injection container creates `NotificationsWorker` with the configured `nats_worker` settings and the domain `NotificationsFacade`.
3. The worker obtains subscriptions dynamically from `NotificationsFacade.get_subscriptions()`.
4. Each NATS message is validated as `CloudEventDTO` by the base worker.
5. `NotificationsWorker` wraps the event in `CreateNotifyRequest` and calls `NotificationsFacade.notify()`.
6. The base worker acknowledges a successful message or negatively acknowledges a failed one.

The base worker also creates or validates the configured JetStream stream, maintains durable pull consumers, propagates tracing context, and drains NATS on shutdown.

## Configuration

The worker expects its settings under the `aspynotifications_worker` root:

```yaml
aspynotifications_worker:
  nats_connection:
    nats_url: "nats://localhost:4222"
  nats_worker:
    name: "aspynotifications-worker"
    subscriptions: []
    stream:
      name: "EVENTS"
      subject: "events.>"
    batch: 1
    ack_wait_seconds: 300
    max_deliver: 2
```

Although `nats_worker.subscriptions` is required by the configuration model, this concrete worker overrides subscription lookup using the notification facade. Its value is still required for model validation.

The worker must also have the `aspynotifications` domain configuration available because its DI container obtains the domain facade. There is currently no default monoconfig directory for `aspynotifications_worker` in this repository, so deployment must provide the worker and domain configuration.

## Command

The package registers the shared worker command:

```bash
python -m aspynotifications_worker.cli.main worker start --help
```

It accepts the common worker options, including `--configfile`, `--nats-url`, verbosity controls, and `--log-format`.

## Boundaries

This package does not implement policy matching, template rendering, provider dispatch, or delivery. It adapts NATS CloudEvents to the domain facade; the domain package owns notification behavior.

## Installation

```bash
make install PACKAGE_NAME=aspynotifications_worker EDITABLE=true
```

or:

```bash
aspymgr pkg install aspynotifications_worker -e
```

## Tests

The package currently contains no automated test files. Tests should mock the facade and verify dynamic subscription lookup, event-to-request conversion, facade delegation, error propagation, and the integration with base-worker acknowledgement behaviour.
