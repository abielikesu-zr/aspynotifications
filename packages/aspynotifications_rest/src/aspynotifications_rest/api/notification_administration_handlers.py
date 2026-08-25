import structlog
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    TemplateDTO,
    UpdateDestinationRequest,
    UpdateNotificationPolicyRequest,
    UpdateTemplateRequest,
)
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
    UpdateNotificationProviderRequest,
)
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)

notification_administration_router = APIRouter(
    prefix="/api/v1",
    tags=["notification-administration"],
)


@notification_administration_router.post("/policies")
async def create_notification_policy(
    body: CreateNotificationPolicyRequest,
    request: Request,
) -> JSONResponse:
    logger.info(
        "New notification policy",
        name=body.name,
        subject=body.subject,
        destinations=body.destinations,
    )
    facade: NotificationsFacade = request.app.state.notifications_facade
    policy: NotificationPolicyDTO = await facade.create_notification_policy(body)
    logger.info(
        "Notification policy created",
        policy_id=policy.id,
        name=policy.name,
    )
    return JSONResponse(content=policy.model_dump())


@notification_administration_router.put("/policies/{policy_id}")
async def update_notification_policy(
    policy_id: str,
    body: UpdateNotificationPolicyRequest,
    request: Request,
) -> JSONResponse:
    if body.id != policy_id:
        raise HTTPException(
            status_code=400,
            detail="Path policy ID does not match request body ID",
        )

    logger.info(
        "Updating notification policy",
        policy_id=body.id,
        subject=body.subject,
        destinations=body.destinations,
    )
    facade: NotificationsFacade = request.app.state.notifications_facade
    policy: NotificationPolicyDTO = await facade.update_notification_policy(body)
    logger.info(
        "Notification policy updated",
        policy_id=policy.id,
        name=policy.name,
    )
    return JSONResponse(content=policy.model_dump())


@notification_administration_router.post("/templates")
async def create_template(
    body: CreateTemplateRequest,
    request: Request,
) -> JSONResponse:
    logger.info("New notification template", name=body.name)
    facade: NotificationsFacade = request.app.state.notifications_facade
    template: TemplateDTO = await facade.create_template(body)
    logger.info("Notification template created", name=template.name)
    return JSONResponse(content=template.model_dump())


@notification_administration_router.put("/templates/{template_name}")
async def update_template(
    template_name: str,
    body: UpdateTemplateRequest,
    request: Request,
) -> JSONResponse:
    if body.name != template_name:
        raise HTTPException(
            status_code=400,
            detail="Path template name does not match request body name",
        )

    logger.info("Updating notification template", name=body.name)
    facade: NotificationsFacade = request.app.state.notifications_facade
    template: TemplateDTO = await facade.update_template(body)
    logger.info("Notification template updated", name=template.name)
    return JSONResponse(content=template.model_dump())


@notification_administration_router.post("/destinations")
async def create_destination(
    body: CreateDestinationRequest,
    request: Request,
) -> JSONResponse:
    logger.info(
        "New notification destination",
        name=body.name,
        provider=body.provider,
        template=body.template,
        destination_type=body.config.type,
        routable=body.routable,
    )
    facade: NotificationsFacade = request.app.state.notifications_facade
    destination: DestinationDTO = await facade.create_destination(body)
    logger.info(
        "Notification destination created",
        destination_id=destination.id,
        name=destination.name,
    )
    return JSONResponse(content=destination.model_dump())


@notification_administration_router.put("/destinations/{destination_id}")
async def update_destination(
    destination_id: str,
    body: UpdateDestinationRequest,
    request: Request,
) -> JSONResponse:
    if body.id != destination_id:
        raise HTTPException(
            status_code=400,
            detail="Path destination ID does not match request body ID",
        )

    logger.info(
        "Updating notification destination",
        destination_id=body.id,
        provider=body.provider,
        template=body.template,
        destination_type=body.config.type,
        routable=body.routable,
    )
    facade: NotificationsFacade = request.app.state.notifications_facade
    destination: DestinationDTO = await facade.update_destination(body)
    logger.info(
        "Notification destination updated",
        destination_id=destination.id,
        name=destination.name,
    )
    return JSONResponse(content=destination.model_dump())


@notification_administration_router.post("/providers")
async def create_notification_provider(
    body: CreateNotificationProviderRequest,
    request: Request,
) -> JSONResponse:
    logger.info(
        "New notification provider",
        name=body.name,
        provider_type=body.provider.type,
    )
    facade: NotificationsFacade = request.app.state.notifications_facade

    provider: NotificationProviderDTO = await facade.create_notification_provider(body)

    logger.info(
        "Notification provider created",
        provider_id=provider.id,
        name=provider.name,
    )
    return JSONResponse(content=provider.model_dump())


@notification_administration_router.put("/providers/{provider_id}")
async def update_notification_provider(
    provider_id: str,
    body: UpdateNotificationProviderRequest,
    request: Request,
) -> JSONResponse:
    if body.id != provider_id:
        raise HTTPException(
            status_code=400,
            detail="Path provider ID does not match request body ID",
        )

    logger.info(
        "Updating notification provider",
        provider_id=body.id,
        provider_type=body.provider.type,
    )
    facade: NotificationsFacade = request.app.state.notifications_facade
    provider: NotificationProviderDTO = await facade.update_notification_provider(body)
    logger.info(
        "Notification provider updated",
        provider_id=provider.id,
        name=provider.name,
    )
    return JSONResponse(content=provider.model_dump())
