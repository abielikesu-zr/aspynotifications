# aspynotifications_sdk

`aspynotifications_sdk` is the Python client for the Notifications REST API. It provides a small `NotificationsSDK` facade, a REST-client adapter, typed configuration, dependency-injection wiring, and transport-specific exceptions.

## Public API

```python
from aspynotifications_dtos.notify_request import CreateNotifyRequest
from aspynotifications_sdk import get_notifications_sdk

sdk = get_notifications_sdk()
result = await sdk.notify(CreateNotifyRequest(...))
```

`NotificationsSDK.notify()` delegates to the configured `INotificationsClientPort`. The built-in implementation is `NotificationsRestClient`, which posts the request to `/api/v1/notifies/`.

## Configuration and initialization

The SDK configuration has this structure:

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

`get_notifications_sdk()` reads the already-registered `aspyconfig` configuration, validates it as `NotificationsSdkConfig`, then wires a singleton dependency-injector container. The caller must register and load `aspyconfig` before calling the accessor. `aspynotifications_cli` performs that initialization for its own command.

The repository supplies defaults in `monoconfig/default/aspynotifications_sdk/aspynotifications_sdk.yaml`.

## REST client and errors

`NotificationsRestClient` joins the configured base URL with the notify path and uses `AspyHttpClient`. It maps transport exceptions to SDK exceptions:

| HTTP client condition | SDK error |
| --- | --- |
| Timeout | `TimeoutError` |
| Connection failure | `TransportError` |
| 404 | `NotFoundError` |
| Bad request | `BadRequestError` |
| Forbidden | `UnauthorizedError` |
| Server error | `ServerError` |
| Other error | `NotificationsClientError` |

`ConflictError` is defined as a client exception type but is not currently produced by the REST-client adapter.

## Boundaries

The SDK accepts the shared `CreateNotifyRequest` DTO and does not implement notification policy evaluation, rendering, or delivery. It is solely a client-side transport boundary.

## Installation

```bash
make install PACKAGE_NAME=aspynotifications_sdk EDITABLE=true
```

or:

```bash
aspymgr pkg install aspynotifications_sdk -e
```

## Tests

The package currently contains no automated test files. Tests should mock `AspyHttpClient` and cover URL construction, request serialization, successful JSON responses, and every exception mapping.
