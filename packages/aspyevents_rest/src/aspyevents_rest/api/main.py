import structlog

from contextlib import asynccontextmanager
from fastapi import FastAPI
from aspyevents_dtos.exceptions import ResourceAlreadyExistsError
from aspyevents_rest.api.error_handlers import resource_already_exists_handler
from aspyevents_sdk import get_events_sdk
from aspyevents_sdk.aspyevents_sdk import EventsSDK
from aspyevents_rest.api.events_handlers import events_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan_context(app: FastAPI):
    logger.info("Initializing application dependencies...")
    app.state.is_started = False
    try:
        sdk: EventsSDK = get_events_sdk()
        app.state.events_sdk = sdk
        app.state.is_started = True
        logger.info("Event Sdk initialized and attached to app.state")
    except Exception as e:
        app.state.is_started = False
        logger.critical("Failed to initialize Events sdk", error=str(e))
        raise RuntimeError("Events Sdk initialization failed") from e

    yield
    app.state.is_started = False
    logger.info("Application shutdown complete.")


events_rest_app = FastAPI(lifespan=lifespan_context)

events_rest_app.include_router(events_router)

events_rest_app.add_exception_handler(
    ResourceAlreadyExistsError,
    resource_already_exists_handler,
)
