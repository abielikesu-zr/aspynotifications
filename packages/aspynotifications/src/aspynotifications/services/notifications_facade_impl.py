from typing import Any

import structlog
from aspynotifications_dtos.notifications_dtos import NotificationSubscriptionsDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest

from aspynotifications.config.notification_facade_config import NotificationFacadeConfig
from aspynotifications.services.cloud_event_service import CloudEventService
from aspynotifications.services.destinations_service import DestinationsService
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications.services.policy_service import NotificationPolicyService
from aspynotifications.services.template_service import TemplateService

logger = structlog.get_logger(__name__)


class NotificationsFacadeImpl(NotificationsFacade):
    def __init__(
        self,
        cloud_event_service: CloudEventService,
        template_service: TemplateService,
        destinations_service: DestinationsService,
        notification_provider_service: NotificationProviderService,
        notification_policy_service: NotificationPolicyService,
        config: dict[str, Any],
    ) -> None:
        self.config = NotificationFacadeConfig.model_validate(config)
        self._cloud_event_service = cloud_event_service
        self._template_service = template_service
        self._destinations_service = destinations_service
        self._notification_provider_service = notification_provider_service
        self._notification_policy_service = notification_policy_service

    async def notify(self, request: CreateNotifyRequest) -> str:
        return "ok"

    async def get_subscriptions(self) -> NotificationSubscriptionsDTO:
        subscriptions = await self._notification_policy_service.get_subscriptions()

        return NotificationSubscriptionsDTO(
            subscriptions=subscriptions,
        )
