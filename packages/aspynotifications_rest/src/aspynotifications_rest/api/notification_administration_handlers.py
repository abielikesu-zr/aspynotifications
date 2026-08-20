from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    TemplateDTO,
)
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
)
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

notification_administration_router = APIRouter(
    prefix="/api/v1",
    tags=["notification-administration"],
)


@notification_administration_router.post("/policies")
async def create_notification_policy(
    body: CreateNotificationPolicyRequest,
    request: Request,
) -> JSONResponse:
    facade: NotificationsFacade = request.app.state.notifications_facade
    policy: NotificationPolicyDTO = await facade.create_notification_policy(body)
    return JSONResponse(content=policy.model_dump())


@notification_administration_router.post("/templates")
async def create_template(
    body: CreateTemplateRequest,
    request: Request,
) -> JSONResponse:
    facade: NotificationsFacade = request.app.state.notifications_facade
    template: TemplateDTO = await facade.create_template(body)
    return JSONResponse(content=template.model_dump())


@notification_administration_router.post("/destinations")
async def create_destination(
    body: CreateDestinationRequest,
    request: Request,
) -> JSONResponse:
    facade: NotificationsFacade = request.app.state.notifications_facade
    destination: DestinationDTO = await facade.create_destination(body)
    return JSONResponse(content=destination.model_dump())


@notification_administration_router.post("/providers")
async def create_notification_provider(
    body: CreateNotificationProviderRequest,
    request: Request,
) -> JSONResponse:
    facade: NotificationsFacade = request.app.state.notifications_facade

    provider: NotificationProviderDTO = await facade.create_notification_provider(body)

    return JSONResponse(content=provider.model_dump())
