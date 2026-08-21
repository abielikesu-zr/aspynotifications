from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal[
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

DataContentType = Literal[
    "application/json",
    "application/cbor",
]


class ErrorData(BaseModel):
    code: str | None = Field(
        default=None,
        description="Error code",
    )
    message: str | None = Field(
        default=None,
        description="Error message",
    )
    stack_trace: str | None = Field(
        default=None,
        description="Error stack trace",
    )
    trace_id: str | None = Field(
        default=None,
        description="Trace identifier",
    )
    reference_id: str | None = Field(
        default=None,
        description="Reference identifier exposed for support",
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional structured error details",
    )


class EventData(BaseModel):
    event: dict[str, Any] | None = Field(
        default=None,
        description="Event-specific data",
    )
    error: ErrorData | None = Field(
        default=None,
        description="Optional structured error information",
    )
    routing: dict[str, Any] | None = Field(
        default=None,
        description="Optional event-specific routing hints",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Optional additional event context",
    )


class CloudEvent(BaseModel):
    specversion: str = Field(
        default="1.0",
        description="CloudEvents specification version",
    )
    type: str = Field(
        ...,
        description="Event type",
    )
    source: str = Field(
        ...,
        description="Event source",
    )
    id: str = Field(
        default="",
        description="Unique event identifier",
    )

    time: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Event timestamp in ISO format",
    )
    subject: str = Field(
        description="Thing the event concerns",
    )
    datacontenttype: DataContentType = Field(
        default="application/json",
        description="Serialization format of the event data",
    )

    severity: Severity = Field(
        default="INFO",
        description="CloudEvent severity extension attribute",
    )

    data: EventData = Field(
        default_factory=EventData,
        description="Application-specific event data",
    )
