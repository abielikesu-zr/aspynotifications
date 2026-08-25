# aspynotifications

Spanish version: [README-aspynotifications_es.md](README-aspynotifications_es.md)

`aspynotifications` is the domain package for the Notification Service. It
provides persistence-backed domain services for CloudEvents, Templates,
NotificationPolicies, Destinations, and NotificationProviders. It also exposes
a facade, template renderers, and provider delivery senders.

## Package information

| Property | Value |
| --- | --- |
| Package | `aspynotifications` |
| Version | `0.1.0` |
| Python | `>=3.12,<3.13` |
| Source | `packages/aspynotifications/src/aspynotifications` |

Package metadata and dependencies are managed by `aspymgr`. Generated
`pyproject.toml` and requirements files must not be edited manually.

## Current capabilities

| Area | Current implementation |
| --- | --- |
| CloudEvents | `CloudEventService` creates, retrieves, lists, and pings persisted CloudEvents. |
| Templates | `TemplateService` creates, updates, retrieves, lists, deletes, and pings templates. |
| Policies | `NotificationPolicyService` provides CRUD, caches policies in a subject trie, and evaluates matching policies through `aspypolicies`. |
| Destinations | `DestinationsService` provides CRUD and pings destination storage. |
| Providers | `NotificationProviderService` provides CRUD, pings provider storage, and selects a sender by provider type. |
| Rendering | `NotificationTemplateRenderer` renders email and Slack template representations through Jinja2. |
| Delivery | Slack and ZeptoMail use their configured HTTP endpoints and return `DeliveryResult(status="accepted")` when the provider accepts the HTTP request. |
| Facade | `NotificationsFacade` exposes `notify` and `get_subscriptions`. `notify` persists the CloudEvent, evaluates matching policies, resolves the union of destinations, renders each message, and delegates delivery to the configured Provider sender. |

## Architecture and public access

The package uses the HexaAs separation of entity, entity-specific store port,
factory, adapter, service, and facade.

```text
configuration
    -> store factories
    -> entity-specific store ports
    -> services
    -> NotificationsFacadeImpl
```

The package entry point provides initialized singleton accessors after the
application has registered and loaded `aspyconfig`:

```python
from aspynotifications import (
    get_cloud_event_service,
    get_destinations_service,
    get_notification_facade,
    get_notification_policy_service,
    get_notification_provider_service,
    get_template_service,
)
```

`get_notifications_config()` validates configuration as
`AspynotificationsAppConfig`, and the dependency-injection container creates
the stores and services. The facade coordinates multi-entity use cases; a
service receives only the store port of its own entity.

## Domain models

| Model | Main responsibility |
| --- | --- |
| `CloudEvent` | CloudEvents 1.0 envelope, severity extension, and `event`/`error`/`routing`/`context` data. |
| `Template` | Named email, Slack, and output-hole template representations with inline or file sources. |
| `NotificationPolicy` | Subject pattern, envelope and destination policies, and destinations selected by a policy match. |
| `Destination` | Named delivery endpoint with a Provider name, template name, routability, and typed endpoint configuration. |
| `NotificationProvider` | Named configured delivery integration with a discriminated provider configuration. |
| `DeliveryResult` | Immutable outcome reported by a sender; the current status is `accepted` after a successful provider HTTP response. |

### Destination configurations

`Destination.config` is discriminated by `type`.

| Type | Configuration model | Fields |
| --- | --- | --- |
| `email` | `EmailDestinationConfig` | `to`, `cc`, `bcc` |
| `slack_channel` | `SlackChannelDestinationConfig` | No additional fields. |
| `output_hole` | `OutputHoleDestinationConfig` | No additional fields. |

`create_destination` receives the typed `DestinationConfig`; it determines the
entity `type` from `config.type`, generates a UUID, rejects a duplicate name,
and persists the entity.

### Notification provider configurations

`NotificationProvider.provider` is discriminated by `type`.

| Type | Configuration | Sender |
| --- | --- | --- |
| `SLACK` | `webhook_url` | `SlackNotificationSender` |
| `ZEPTOMAIL` | `from_address`, optional `from_name`, `send_mail_token` | `ZeptoMailNotificationSender` |

`NotificationProviderService.send(provider, destination, message)` resolves the
sender through the `notification_sender` plugin group. It does not verify that
a Provider type is compatible with a Destination type; callers must provide a
valid pairing.

## Persistence adapters

Each persisted entity has an entity-specific store port and a factory that
selects an adapter from its storage configuration.

| Store group | LocalFS adapter | MongoDB adapter |
| --- | --- | --- |
| `cloud_event_store` | `CloudEventFileStoreAdapter` | `CloudEventMongoStoreAdapter` |
| `template_store` | `TemplateFileStoreAdapter` | `TemplateMongoStoreAdapter` |
| `notification_policy_store` | `NotificationPolicyFileStoreAdapter` | `NotificationPolicyStoreMongoAdapter` |
| `destinations_store` | `DestinationsStoreAdapter` | `DestinationsMongoStoreAdapter` |
| `notification_provider_store` | `NotificationProviderFileStoreAdapter` | `NotificationProviderStoreMongoAdapter` |

The adapters are registered lazily in
`resources/config/aspynotifications_plugins.yaml`. For the observed exception
and structured-logging differences between these stores, see
[store-pattern.md](store-pattern.md).

## Rendering and delivery limits

`NotificationTemplateRenderer` currently supports only `email` and
`slack_channel` destinations. Email and Slack renderers use Jinja2 and write a
rendered YAML artifact under `var/rendered/`.

The current facade does not connect CloudEvent ingestion, policy matching,
template lookup, rendering, Provider resolution, and delivery. Those components
exist independently; end-to-end notification delivery remains pending.

## Configuration

The root key is `aspynotifications`. The repository provides the default
configuration in:

```text
monoconfig/default/aspynotifications/aspynotifications.yaml
```

It declares storage and service configuration for policies, destinations,
templates, CloudEvents, notification providers, the sender HTTP client, and the
facade. A typical LocalFS store configuration is:

```yaml
aspynotifications:
  destinations_store:
    adapter:
      type: LOCALFS
      config:
        data_dir: ./var/aspynotifications/destinations_store
  destinations_service:
    keep: "keep"
```

`AspynotificationsAppParams` also requires `policy_store`, `template_store`,
`cloud_event_store`, and `notification_provider_store`, each using the shared
`StorageAdapterConfig` with `LOCALFS` or `MONGODB`.

## Installation

From the repository root, install the package in editable mode:

```bash
make install PACKAGE_NAME=aspynotifications EDITABLE=true
```

The equivalent package-manager command is:

```bash
aspymgr pkg install aspynotifications -e
```

## Tests

The package contains async pytest suites for destination services and LocalFS
storage, provider creation, and provider sender selection.

```bash
source .venv/bin/activate
python -m pytest packages/aspynotifications/tests -q
```

Current test status, verified on 2026-08-18:

```text
16 passed, 9 failed
```

The nine failures are in the Destination suites. They still call the previous
`create_destination(..., destination_type=...)` signature, while the current
service accepts `config: DestinationConfig` and derives the type from
`config.type`. The provider and sender tests pass. MongoDB integration tests
are not present.

## Package structure

```text
packages/aspynotifications/src/aspynotifications/
├── adapters/                 # storage, rendering, context, and sender adapters
├── config/                   # typed application and service configuration
├── containers/               # dependency-injection composition root
├── entities/                 # domain models
├── factories/                # store and sender selection
├── ports/                    # store, renderer, and sender contracts
├── resources/config/         # lazy plugin registrations
└── services/                 # domain services and public facade
```
