from __future__ import annotations

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = structlog.get_logger(__name__)


async def resource_already_exists_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)},
    )
