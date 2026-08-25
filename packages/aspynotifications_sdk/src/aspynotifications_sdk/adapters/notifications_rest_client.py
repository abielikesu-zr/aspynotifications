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
from aspyplugs.registry import register_plugin
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    TemplateDTO,
    UpdateTemplateRequest,
)
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
)

from aspynotifications_sdk.entities.config import RestClientConfig
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


@register_plugin("notifications_client", "REST")
class NotificationsRestClient(INotificationsClientPort):
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
            raise NotificationsClientError(f"Unexpected error: {e!s}") from e

    async def notify(self, request: CreateNotifyRequest) -> str:
        logger.debug("notify rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/notifies/",
            payload=request.model_dump(),
        )
        return resp.json()

    async def create_notification_policy(
        self,
        request: CreateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO:
        logger.debug("create notification policy rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/policies",
            payload=request.model_dump(),
        )
        return NotificationPolicyDTO.model_validate(resp.json())

    async def create_template(self, request: CreateTemplateRequest) -> TemplateDTO:
        logger.debug("create template rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/templates",
            payload=request.model_dump(),
        )
        return TemplateDTO.model_validate(resp.json())

    async def update_template(self, request: UpdateTemplateRequest) -> TemplateDTO:
        logger.debug("update template rest client request", request=request)
        resp = await self._handle_request(
            "PUT",
            f"/api/v1/templates/{request.name}",
            payload=request.model_dump(mode="json"),
        )
        return TemplateDTO.model_validate(resp.json())

    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO:
        logger.debug("create destination rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/destinations",
            payload=request.model_dump(),
        )
        return DestinationDTO.model_validate(resp.json())

    async def create_notification_provider(
        self,
        request: CreateNotificationProviderRequest,
    ) -> NotificationProviderDTO:
        logger.debug("create notification provider rest client request", request=request)
        resp = await self._handle_request(
            "POST",
            "/api/v1/providers",
            payload=request.model_dump(),
        )
        return NotificationProviderDTO.model_validate(resp.json())
