from typing import Any

import structlog
from aspynotifications_dtos.notifications_dtos import NotificationSubscriptionsDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest

from aspynotifications.config.notification_facade_config import NotificationFacadeConfig
from aspynotifications.entities.cloud_event import CloudEvent
from aspynotifications.services.cloud_event_service import CloudEventService
from aspynotifications.services.destinations_service import DestinationsService
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications.services.notify_renderer import NotificationTemplateRenderer
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
        notification_template_renderer: NotificationTemplateRenderer,
        config: dict[str, Any],
    ) -> None:
        self.config = NotificationFacadeConfig.model_validate(config)
        self._cloud_event_service = cloud_event_service
        self._template_service = template_service
        self._destinations_service = destinations_service
        self._notification_provider_service = notification_provider_service
        self._notification_policy_service = notification_policy_service
        self._notification_template_renderer = notification_template_renderer

    async def notify(self, request: CreateNotifyRequest) -> str:
        cloud_event = CloudEvent.model_validate(
            request.event.model_dump(exclude_none=True)
        )
        await self._cloud_event_service.create_cloud_event(cloud_event)

        event = cloud_event.model_dump(exclude_none=True)
        context = self._notification_policy_service.event_to_context(event)
        policies = await self._notification_policy_service.find_matching_policies(event)

        destination_names: list[str] = []
        seen_destination_names: set[str] = set()
        for policy in policies:
            for destination_name in policy.destinations:
                if destination_name not in seen_destination_names:
                    seen_destination_names.add(destination_name)
                    destination_names.append(destination_name)

        for destination_name in destination_names:
            destination = await self._destinations_service.get_destination_by_name(
                destination_name
            )
            if destination is None:
                raise LookupError(f"Destination not found: {destination_name}")

            template = await self._template_service.get_template_by_name(
                destination.template
            )
            if template is None:
                raise LookupError(f"Template not found: {destination.template}")

            provider = (
                await self._notification_provider_service.get_notification_provider_by_name(
                    destination.provider
                )
            )
            if provider is None:
                raise LookupError(f"Provider not found: {destination.provider}")

            message = self._notification_template_renderer.render(
                destination=destination,
                template=template,
                context=context,
            )
            await self._notification_provider_service.send(
                provider=provider,
                destination=destination,
                message=message,
            )

        logger.info(
            "Notification delivered",
            event_id=cloud_event.id,
            policy_count=len(policies),
            destination_count=len(destination_names),
        )
        return "ok"

    async def get_subscriptions(self) -> NotificationSubscriptionsDTO:
        subscriptions = await self._notification_policy_service.get_subscriptions()

        return NotificationSubscriptionsDTO(
            subscriptions=subscriptions,
        )
