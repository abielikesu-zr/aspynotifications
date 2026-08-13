from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

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
    code: Optional[str] = Field(
        default=None,
        description="Error code",
    )
    message: Optional[str] = Field(
        default=None,
        description="Error message",
    )
    stack_trace: Optional[str] = Field(
        default=None,
        description="Error stack trace",
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="Trace identifier",
    )
    reference_id: Optional[str] = Field(
        default=None,
        description="Reference identifier exposed for support",
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional structured error details",
    )


class EventData(BaseModel):
    event: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Event-specific data",
    )
    error: Optional[ErrorData] = Field(
        default=None,
        description="Optional structured error information",
    )
    routing: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional event-specific routing hints",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional event context",
    )


class CloudEvent(BaseModel):
    specversion: Literal["1.0"] = Field(
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
        ...,
        description="Unique event identifier",
    )
    time: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Event timestamp in ISO format",
    )
    subject: Optional[str] = Field(
        default=None,
        description="Thing the event concerns",
    )
    datacontenttype: DataContentType = Field(
        default="application/json",
        description="Serialization format of the event data",
    )

    severity: Optional[Severity] = Field(
        default=None,
        description="CloudEvent severity extension attribute",
    )

    data: EventData = Field(
        default_factory=EventData,
        description="Application-specific event data",
    )