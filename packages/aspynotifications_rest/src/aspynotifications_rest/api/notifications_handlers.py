import structlog
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)

notifications_router = APIRouter(prefix="/api/v1/notifies", tags=["notifications"])


@notifications_router.post("/")
async def notify(body: CreateNotifyRequest, request: Request) -> JSONResponse:
    request_dto = CreateNotifyRequest(event=body.event)

    logger.info(
        "New notification", type=request_dto.event.type, source=request_dto.event.source
    )

    facade: NotificationsFacade = request.app.state.notifications_facade
    result: str = await facade.notify(request_dto)
    logger.info("Notification sent")

    return JSONResponse(content=result)
