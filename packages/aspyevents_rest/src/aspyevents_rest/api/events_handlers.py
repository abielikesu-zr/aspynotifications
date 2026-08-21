import structlog
from aspyevents_dtos.publish_event_request import PublishEventRequest
from aspyevents_sdk.aspyevents_sdk import EventsSDK
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)

events_router = APIRouter(prefix="/api/v1/publishes", tags=["events_rest"])


@events_router.post("/")
async def publish(body: PublishEventRequest, request: Request) -> JSONResponse:
    request_dto = PublishEventRequest(event=body.event)

    logger.info(
        "New events", type=request_dto.event.type, source=request_dto.event.source
    )

    sdk: EventsSDK = request.app.state.events_sdk
    result: str = await sdk.publish(request_dto)
    logger.info("Events sent")

    return JSONResponse(content=result)
