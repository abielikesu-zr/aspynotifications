from typing import Any, Dict

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

from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest
from aspynotifications_sdk.entities.config import NotificationsClientConfig
from aspynotifications_sdk.errors import (
    BadRequestError,
    NotFoundError,
    NotificationsClientError,
    ServerError,
    TimeoutError,
    TransportError,
    UnauthorizedError,
)
from aspynotifications_sdk.ports.notifications_client_port import (
    INotificationsClientPort,
)

logger = structlog.get_logger(__name__)


class NotificationsRestClient(INotificationsClientPort):

    def __init__(self, config: Dict[str, Any], http_client: AspyHttpClient):
        self.config = NotificationsClientConfig.model_validate(config)
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
            raise NotFoundError(f"Resource not found: {str(e)}") from e
        except HttpClientBadRequestError as e:
            raise BadRequestError(f"Bad Request: {str(e)}") from e
        except HttpClientForbiddenError as e:
            raise UnauthorizedError(f"Access forbidden: {str(e)}") from e
        except HttpClientServerError as e:
            raise ServerError(f"Internal server error: {str(e)}") from e
        except Exception as e:
            raise NotificationsClientError(f"Unexpected error: {str(e)}") from e

    async def notify(self, request: CreateNotifyRequest) -> str:
        logger.debug("notify rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/notifies/",
            payload=request.model_dump(),
        )
        return resp.json()
