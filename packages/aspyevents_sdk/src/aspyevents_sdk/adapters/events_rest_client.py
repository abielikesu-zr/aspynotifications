from typing import Any

import structlog
from aspyadapters.adapters.http_client import AspyHttpClient
from aspyadapters.adapters.http_exceptions import (
    HttpClientBadRequestError,
    HttpClientConnectionError,
    HttpClientForbiddenError,
    HttpClientNotFoundError,
    HttpClientServerError,
    HttpClientTimeoutError,
)
from aspyevents_dtos.publish_event_request import PublishEventRequest
from aspyplugs.registry import register_plugin

from aspyevents_sdk.entities.config import RestClientConfig
from aspyevents_sdk.errors import (
    BadRequestError,
    NotFoundError,
    EventsClientError,
    ServerError,
    TimeoutError,
    TransportError,
    UnauthorizedError,
)
from aspyevents_sdk.ports.events_client_port import (
    IEventsClientPort,
)

logger = structlog.get_logger(__name__)


@register_plugin("events_client", "REST")
class EventsRestClient(IEventsClientPort):
    def __init__(self, config: dict[str, Any], http_client: AspyHttpClient):
        self.config = RestClientConfig.model_validate(config)
        self._base_url = self.config.base_url
        self._http = http_client

    def _url(self, path: str) -> str:
        return f"{str(self._base_url).rstrip('/')}/{path.lstrip('/')}"

    async def _handle_request(self, method: str, path: str, **kwargs) -> Any:
        try:
            if method == "GET":
                return await self._http.get(self._url(path), **kwargs)
            elif method == "POST":
                return await self._http.post(self._url(path), **kwargs)
            elif method == "PUT":
                return await self._http.put(self._url(path), **kwargs)
            elif method == "DELETE":
                return await self._http.delete(self._url(path), **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method {method}")
        except HttpClientTimeoutError as e:
            raise TimeoutError(f"Request to {path} timed out") from e
        except HttpClientConnectionError as e:
            raise TransportError(f"Connection error calling {path}") from e
        except HttpClientNotFoundError as e:
            raise NotFoundError(f"Resource not found: {e!s}") from e
        except HttpClientBadRequestError as e:
            raise BadRequestError(f"Bad Request: {e!s}") from e
        except HttpClientForbiddenError as e:
            raise UnauthorizedError(f"Access forbidden: {e!s}") from e
        except HttpClientServerError as e:
            raise ServerError(f"Internal server error: {e!s}") from e
        except Exception as e:
            raise EventsClientError(f"Unexpected error: {e!s}") from e

    async def publish(self, request: PublishEventRequest) -> str:
        logger.debug("notify rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/notifies/",
            payload=request.model_dump(),
        )
        return resp.json()
