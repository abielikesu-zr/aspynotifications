# aspynotifications_rest

`aspynotifications_rest` exposes the Notifications facade as a FastAPI application. It owns the HTTP boundary and REST-server configuration; domain processing remains in the `aspynotifications` package.

## HTTP API

| Method | Path | Request | Current response |
| --- | --- | --- | --- |
| `POST` | `/api/v1/notifies/` | `CreateNotifyRequest` | JSON representation of the string returned by `NotificationsFacade.notify` |

The endpoint validates the request through FastAPI and Pydantic, obtains the facade attached to `app.state`, and delegates notification processing to it.

## Application lifecycle

`notifications_rest_app` uses a FastAPI lifespan handler. At startup it obtains `get_notification_facade()` from the domain package and stores it in `app.state.notifications_facade`. Startup fails if facade initialization fails; the application does not continue with an unavailable facade.

The command module integrates the application with `aspyrest`'s `rest_start_command`:

```bash
python -m aspynotifications_rest.cli.main --help
```

Use the command help provided by the installed `aspyrest` runtime to see its server start options.

## Configuration

`AspynotificationsRestAppConfig` reads the `aspynotifications_rest` root. Its server settings default to:

```yaml
aspynotifications_rest:
  rest_server:
    host: "127.0.0.1"
    port: 50000
```

The repository default configuration directory for this package additionally contains the domain package configuration, under `monoconfig/default/aspynotifications_rest/aspynotifications.yaml`. It configures the facade's stores and services with LocalFS adapters. Both configuration roots are needed for a working REST application.

## Boundaries

The package does not implement notification policy matching, destination rendering, provider dispatch, or persistence. Those responsibilities belong to the domain facade and its services.

## Installation

```bash
make install PACKAGE_NAME=aspynotifications_rest EDITABLE=true
```

or:

```bash
aspymgr pkg install aspynotifications_rest -e
```

## Tests

The package currently contains no automated test files. Appropriate tests should cover successful application startup, facade initialization failure, request validation, and delegation of the `POST /api/v1/notifies/` endpoint to the facade.
