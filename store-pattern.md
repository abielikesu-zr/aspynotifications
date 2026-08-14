# Store Pattern

## Purpose and scope

This document records the LocalFS and MongoDB store-adapter pattern observed in
`aspynotifications` on 2026-08-14. It covers the ten concrete adapters below,
with special attention to exception handling and structured logging.

It is an evidence-based pattern record: common behavior is identified as such,
and differences between implementations are preserved explicitly. A behavior
marked as a difference is not a project-wide standard until it is deliberately
adopted.

## Inventory and Git authorship

| Entity | LocalFS adapter | MongoDB adapter | Git authorship by current lines |
| --- | --- | --- | --- |
| CloudEvent | `cloud_event/cloud_event_file_adapter.py` | `cloud_event/cloud_event_mongo_adapter.py` | Jose Navarro: both files |
| Template | `template/template_file_adapter.py` | `template/template_mongo_adapter.py` | Jose Navarro: both files |
| Destination | `destinations_file_adapter.py` | `destinations_mongo_adapter.py` | LocalFS: Afranio Solano, except 4 later lines by Abidis Solano; MongoDB: Afranio Solano |
| NotificationPolicy | `policy_file_store.py` | `policy_mongo_store.py` | Abidis Solano: both files |
| NotificationProvider | `provider_file_store.py` | `provider_mongo_store.py` | Abidis Solano: both files |

The current-line attribution is: Abidis Solano 696 lines, Afranio Solano 227
lines, and Jose Navarro 295 lines across this adapter corpus.

## Shared structural pattern

Every adapter follows these common structural rules:

1. It inherits its entity-specific store port and exactly one generic storage
   adapter: `GenericLocalFSAdapter` or `GenericMongoAdapter`.
2. It registers itself in the entity-specific plugin group with `LOCALFS` or
   `MONGODB` using `@register_plugin`.
3. `get_model_class()` returns the Pydantic entity model.
4. LocalFS stores persist `<entity-id>.json` when the entity has an `id`;
   Templates use their `name` as their persistence key.
5. MongoDB stores define `get_collection_name()` and pass the canonical key to
   the generic `save`, `load`, and `delete` operations.
6. Stores contain persistence translation only. They do not implement domain
   rules, coordinate other entities, or call services.
7. `ping()` delegates to `ping_resource()` in every adapter, although the
   behavior when that operation raises is not currently uniform.

## Exception handling pattern

### Meaning of absence

Absence is treated as a normal query result, not as an operational error:

| Backend | Read-by-ID exception | Returned value |
| --- | --- | --- |
| LocalFS | `FileNotFoundError` | `None` |
| MongoDB | `NotFoundError` | `None` |

The same idea is used by the MongoDB policy and provider adapters for
read-by-name. LocalFS policy and provider adapters obtain the name index and
return `None` when the result list is empty.

### Corrupt persisted data

The stronger repeated behavior, used by Destination, NotificationPolicy, and
NotificationProvider adapters, is:

1. Catch `pydantic.ValidationError` from `load`, `find`, or `find_one`.
2. Emit a structured log that identifies corruption and includes the lookup
   key when one exists.
3. Raise `ValueError` chained from the validation failure.

This distinguishes invalid persisted data from an unavailable storage backend.
CloudEvent and Template adapters instead log the validation failure and use a
bare `raise`, so their caller receives `ValidationError`. That is a documented
difference, not the repeated translation pattern.

### Unexpected persistence failures

Where an adapter catches an unexpected `Exception`, it logs the operation,
entity identity when available, and `error=str(error)`. The catch-all coverage
is not uniform: CloudEvent and Template do not add an unexpected-error branch
around their read-by-ID operation, so such failures propagate without a local
log entry.

Destination, NotificationPolicy, and NotificationProvider adapters translate
the failure to a new contextual `Exception` using `raise ... from error`.
This preserves the original exception as the cause while adding the failed
operation and entity key. CloudEvent and Template adapters re-raise the
original exception for save and delete, but wrap list failures with a generic
contextual `Exception`.

### Delete and ping are not yet uniform

The current implementations differ in two important contracts:

| Operation | Observed behavior |
| --- | --- |
| Delete of a missing LocalFS record | Destination returns successfully; NotificationPolicy and NotificationProvider log and raise because they do not catch `FileNotFoundError`; CloudEvent and Template re-raise it. |
| Delete of a missing MongoDB record | NotificationPolicy and NotificationProvider return successfully after `NotFoundError`; Destination, CloudEvent, and Template do not handle it explicitly. |
| `ping_resource()` raises | CloudEvent and Template log `PING error` and return `False`; Destination, NotificationPolicy, and NotificationProvider propagate the exception. |

No single delete-idempotency or ping-failure policy is established by the
current code. Any future standard must choose one behavior and apply it to all
ten adapters before it is considered uniform.

## Structured logging pattern

Every store uses `structlog`, but the level and traceback payload differ by
author family.

| Family | Level for persistence failures | Context | Traceback payload |
| --- | --- | --- | --- |
| Jose Navarro: CloudEvent and Template | `logger.error` | Operation, entity key or name, `error=str(e)` | `exc_info=e` |
| Afranio Solano: Destination | `logger.error` | Operation, `destination_id` or `destination_name`, `error=str(error)` | Not supplied |
| Abidis Solano: NotificationPolicy and NotificationProvider LocalFS | `logger.debug` | Operation, `policy_id`/`provider_id` or name, `error=str(e)` | `exc_info=e` |
| Abidis Solano: NotificationPolicy and NotificationProvider MongoDB | `logger.error` | Operation, identifier or name, `error=str(e)` | Not supplied |

The observable common minimum is therefore: a stable operation message,
`error=str(exception)`, and the entity key or lookup name whenever available.
Log level and `exc_info` are not uniform today.

## Per-author implementation differences

### Jose Navarro — CloudEvent and Template

- Uses concise adapters without class or method docstrings.
- Uses `logger.error(..., exc_info=e)` for every caught failure.
- Treats `FileNotFoundError` and `NotFoundError` on reads as `None`.
- Re-raises original errors for save, validation, and delete.
- Wraps only list failures with a contextual generic `Exception`.
- Converts a failed `ping_resource()` into `False` after logging it.

### Afranio Solano — Destination

- Uses typed collection signatures and concise class docstrings.
- Uses `logger.error` with a specific destination identifier/name and without
  `exc_info`.
- Translates `ValidationError` into `ValueError` and unexpected errors into a
  chained contextual `Exception`.
- Handles a missing LocalFS record on delete as a successful no-op.
- Delegates `ping_resource()` without a local exception handler.

### Abidis Solano — NotificationPolicy and NotificationProvider

- Uses extensive class and method docstrings and entity-specific operation
  names.
- LocalFS adapters use `logger.debug(..., exc_info=e)` for persistence
  failures; MongoDB adapters use `logger.error` without `exc_info`.
- Translates `ValidationError` to `ValueError` and other failures to chained
  contextual `Exception` values.
- MongoDB adapters treat `NotFoundError` as `None` for reads and as a no-op for
  delete.
- LocalFS deletes do not catch `FileNotFoundError`.
- Delegates `ping_resource()` and propagates any failure.

## Review checklist for a new store

Use this checklist to compare a new adapter with the observed pattern and to
make any deliberate contract decision visible:

- [ ] The adapter implements only its entity-specific port and one generic
  backend adapter.
- [ ] The plugin group and `LOCALFS`/`MONGODB` label match the corresponding
  factory.
- [ ] `get_model_class()` and, for MongoDB, `get_collection_name()` identify
  the correct entity and collection.
- [ ] A missing record has an explicit normal-result policy for both read and
  delete.
- [ ] `ValidationError` has an explicit corruption policy and does not become
  indistinguishable from an infrastructure failure.
- [ ] Every unexpected persistence failure logs the operation, entity key or
  lookup key, and `error=str(error)` before propagating or translating it.
- [ ] The chosen log level and `exc_info` behavior are consistent with the
  adopted store contract.
- [ ] The original exception remains available through exception chaining when
  a new contextual exception is raised.
- [ ] `ping()` has an explicit contract: propagate storage failure or return
  `False`; do not leave this accidental.
