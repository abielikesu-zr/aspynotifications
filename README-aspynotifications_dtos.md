# aspynotifications_dtos

`aspynotifications_dtos` contains the Pydantic data-transfer objects shared by the REST API, SDK, CLI, and workers. It has no persistence, transport, configuration loader, or service logic.

## DTOs

| DTO | Purpose |
| --- | --- |
| `CloudEventDTO` | CloudEvents 1.0 envelope used throughout the notification flow. |
| `EventDataDTO` | Application event payload plus optional error, routing, and context sections. |
| `ErrorDataDTO` | Structured error details: code, message, stack trace, trace and reference IDs, and arbitrary details. |
| `CreateNotifyRequest` | Top-level notification request containing a `CloudEventDTO`. |
| `NotificationSubscriptionsDTO` | A list of NATS subscription subjects returned by notification policy matching. |

## CloudEventDTO

Required fields are `type` and `source`. The model supplies these defaults:

| Field | Default or allowed values |
| --- | --- |
| `specversion` | `"1.0"` |
| `time` | Current UTC time in ISO 8601 format |
| `datacontenttype` | `"application/json"` or `"application/cbor"`; defaults to JSON |
| `data` | Empty `EventDataDTO` |
| `severity` | Optional: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |

Optional CloudEvents extensions are `traceparent`, `tracestate`, and `severity`. Event-specific information belongs under `data.event`; optional error, routing, and context information belong in their corresponding `data` fields.

## Example

```python
from aspynotifications_dtos.cloud_event_dto import CloudEventDTO, EventDataDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest

request = CreateNotifyRequest(
    event=CloudEventDTO(
        type="incident.created",
        source="example-service",
        data=EventDataDTO(event={"incident_id": "incident-123"}),
    )
)
```

## Installation

```bash
make install PACKAGE_NAME=aspynotifications_dtos EDITABLE=true
```

or:

```bash
aspymgr pkg install aspynotifications_dtos -e
```

## Tests

The package currently contains no automated test files. Tests should validate the required CloudEvents fields, literal restrictions, default timestamp generation, nested error data, and request serialization/deserialization.
