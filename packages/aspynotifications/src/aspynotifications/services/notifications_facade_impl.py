from typing import Any

import structlog
from aspyevents.entities.cloud_event import CloudEvent
from aspynotifications_dtos.exceptions import ResourceAlreadyExistsError
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    NotificationSubscriptionsDTO,
    TemplateDTO,
)
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
)
from aspypolicies.entities.aspy_policy import AspyPolicy
from pydantic import TypeAdapter

from aspynotifications.config.destination_config import DestinationConfig
from aspynotifications.config.notification_facade_config import NotificationFacadeConfig
from aspynotifications.entities.exceptions import DestinationAlreadyExistsError
from aspynotifications.entities.template import Template
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
        template_service: TemplateService,
        destinations_service: DestinationsService,
        notification_provider_service: NotificationProviderService,
        notification_policy_service: NotificationPolicyService,
        notification_template_renderer: NotificationTemplateRenderer,
        config: dict[str, Any],
    ) -> None:
        self.config = NotificationFacadeConfig.model_validate(config)
        self._template_service = template_service
        self._destinations_service = destinations_service
        self._notification_provider_service = notification_provider_service
        self._notification_policy_service = notification_policy_service
        self._notification_template_renderer = notification_template_renderer

    async def notify(self, request: CreateNotifyRequest) -> str:
        logger.debug("Processing notification request")

        cloud_event = CloudEvent.model_validate(
            request.event.model_dump(exclude_none=True)
        )

        logger.debug(
            "CloudEvent validated",
            event_id=cloud_event.id,
            event_type=cloud_event.type,
            source=cloud_event.source,
            subject=cloud_event.subject,
        )

        event = cloud_event.model_dump(exclude_none=True)

        logger.debug(
            "Building notification policy context",
            event_id=cloud_event.id,
        )

        context = self._notification_policy_service.event_to_context(event)

        logger.debug(
            "Notification policy context built",
            event_id=cloud_event.id,
            context=context,
        )

        logger.debug(
            "Finding matching notification policies",
            event_id=cloud_event.id,
            event_type=cloud_event.type,
            subject=cloud_event.subject,
        )

        policies = await self._notification_policy_service.find_matching_policies(event)

        logger.debug(
            "Notification policies matched",
            event_id=cloud_event.id,
            policy_count=len(policies),
            policies=[policy.name for policy in policies],
        )

        destination_names: list[str] = []
        seen_destination_names: set[str] = set()

        for policy in policies:
            logger.debug(
                "Processing notification policy destinations",
                event_id=cloud_event.id,
                policy=policy.name,
                destinations=policy.destinations,
            )

            for destination_name in policy.destinations:
                if destination_name not in seen_destination_names:
                    seen_destination_names.add(destination_name)
                    destination_names.append(destination_name)

        logger.debug(
            "Notification destinations resolved from policies",
            event_id=cloud_event.id,
            destination_count=len(destination_names),
            destinations=destination_names,
        )

        for destination_name in destination_names:
            logger.debug(
                "Loading notification destination",
                event_id=cloud_event.id,
                destination=destination_name,
            )

            destination = await self._destinations_service.get_destination_by_name(
                destination_name
            )

            if destination is None:
                logger.error(
                    "Notification destination not found",
                    event_id=cloud_event.id,
                    destination=destination_name,
                )
                raise LookupError(f"Destination not found: {destination_name}")

            logger.debug(
                "Notification destination loaded",
                event_id=cloud_event.id,
                destination=destination.name,
                template=destination.template,
                provider=destination.provider,
            )

            logger.debug(
                "Loading notification template",
                event_id=cloud_event.id,
                template=destination.template,
            )

            template = await self._template_service.get_template_by_name(
                destination.template
            )

            if template is None:
                logger.error(
                    "Notification template not found",
                    event_id=cloud_event.id,
                    template=destination.template,
                )
                raise LookupError(f"Template not found: {destination.template}")

            logger.debug(
                "Notification template loaded",
                event_id=cloud_event.id,
                template=template.name,
            )

            logger.debug(
                "Loading notification provider",
                event_id=cloud_event.id,
                provider=destination.provider,
            )

            provider = await self._notification_provider_service.get_notification_provider_by_name(
                destination.provider
            )

            if provider is None:
                logger.error(
                    "Notification provider not found",
                    event_id=cloud_event.id,
                    provider=destination.provider,
                )
                raise LookupError(f"Provider not found: {destination.provider}")

            logger.debug(
                "Notification provider loaded",
                event_id=cloud_event.id,
                provider=provider.name,
                provider_type=provider.provider.type,
            )

            logger.debug(
                "Rendering notification",
                event_id=cloud_event.id,
                destination=destination.name,
                template=template.name,
                provider=provider.name,
            )

            message = self._notification_template_renderer.render(
                destination=destination,
                template=template,
                context=context,
            )

            logger.debug(
                "Notification rendered",
                event_id=cloud_event.id,
                destination=destination.name,
            )

            logger.debug(
                "Sending notification",
                event_id=cloud_event.id,
                destination=destination.name,
                provider=provider.name,
                provider_type=provider.provider.type,
            )

            await self._notification_provider_service.send(
                provider=provider,
                destination=destination,
                message=message,
            )

            logger.debug(
                "Notification sent",
                event_id=cloud_event.id,
                destination=destination.name,
                provider=provider.name,
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

    async def create_notification_policy(
        self,
        request: CreateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO:
        policy = await self._notification_policy_service.create_notification_policy(
            name=request.name,
            subject=request.subject,
            envelope_policies=[
                AspyPolicy.model_validate(policy.model_dump())
                for policy in request.envelope_policies
            ],
            destination_policies=[
                AspyPolicy.model_validate(policy.model_dump())
                for policy in request.destination_policies
            ],
            destinations=request.destinations,
        )
        return NotificationPolicyDTO.model_validate(policy.model_dump())

    async def create_template(self, request: CreateTemplateRequest) -> TemplateDTO:
        template = Template.model_validate(request.model_dump())
        created_template = await self._template_service.create_template(template)
        return TemplateDTO.model_validate(created_template.model_dump())

    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO:
        config = TypeAdapter(DestinationConfig).validate_python(
            request.config.model_dump()
        )
        try:
            destination = await self._destinations_service.create_destination(
                name=request.name,
                provider=request.provider,
                template=request.template,
                routable=request.routable,
                config=config,
            )
        except DestinationAlreadyExistsError as exc:
            raise ResourceAlreadyExistsError(str(exc)) from exc
        return DestinationDTO.model_validate(destination.model_dump())

    async def create_notification_provider(
        self,
        request: CreateNotificationProviderRequest,
    ) -> NotificationProviderDTO:
        provider = (
            await self._notification_provider_service.create_notification_provider(
                name=request.name,
                provider_type=request.provider.type,
                config=request.provider.config.model_dump(),
            )
        )

        return NotificationProviderDTO.model_validate(provider.model_dump())
