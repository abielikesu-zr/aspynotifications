"""POC de un servidor HTTP que entrega eventos Server-Sent Events (SSE)."""

import asyncio
import json
from collections.abc import AsyncIterator
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


app = FastAPI(title="SSE notifications POC")
subscribers: dict[str, set[asyncio.Queue["Notification"]]] = {}


class Notification(BaseModel):
    """Notificación aceptada por el POC y distribuida a clientes SSE conectados."""

    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: str = "info"
    recipient_user_id: str = Field(min_length=1)


async def notification_events(user_id: str) -> AsyncIterator[str]:
    """Mantiene una cola por cliente para entregar notificaciones bajo demanda."""
    queue: asyncio.Queue[Notification] = asyncio.Queue()
    subscribers.setdefault(user_id, set()).add(queue)
    try:
        while True:
            notification = await queue.get()
            event_id = str(uuid4())
            yield (
                f"id: {event_id}\n"
                "event: notification\n"
                f"data: {json.dumps(notification.model_dump(), ensure_ascii=False)}\n\n"
            )
    finally:
        user_subscribers = subscribers.get(user_id)
        if user_subscribers is not None:
            user_subscribers.discard(queue)
            if not user_subscribers:
                subscribers.pop(user_id, None)


@app.post("/notifications", status_code=202)
async def publish_notification(notification: Notification) -> dict[str, int]:
    """Recibe una notificación desde otro proceso y la entrega a cada cliente conectado."""
    recipient_subscribers = subscribers.get(notification.recipient_user_id, set())
    for queue in tuple(recipient_subscribers):
        queue.put_nowait(notification)
    return {"accepted": 1, "connected_clients": len(recipient_subscribers)}


@app.get("/notifications/stream")
async def notifications_stream(user_id: str = Query(min_length=1)) -> StreamingResponse:
    """Mantiene una respuesta HTTP abierta y entrega notificaciones por SSE."""
    return StreamingResponse(
        notification_events(user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
