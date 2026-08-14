from contextlib import asynccontextmanager

import structlog
from aspynotifications import get_notification_facade
from aspynotifications.services.notifications_facade import NotificationsFacade
from fastapi import FastAPI

from aspynotifications_rest.api.notifications_handlers import notifications_router

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan_context(app: FastAPI):
    logger.info("Initializing application dependencies...")
    app.state.is_started = False
    try:
        notifications_facade: NotificationsFacade = get_notification_facade()
        app.state.notifications_facade = notifications_facade
        app.state.is_started = True
        logger.info("Notifications facade initialized and attached to app.state")
    except Exception as e:
        app.state.is_started = False
        logger.critical("Failed to initialize notifications facade", error=str(e))
        raise RuntimeError("Notifications facade initialization failed") from e

    yield
    app.state.is_started = False
    logger.info("Application shutdown complete.")


notifications_rest_app = FastAPI(lifespan=lifespan_context)

notifications_rest_app.include_router(notifications_router)
