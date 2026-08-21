from aspyevents_dtos.cloud_event_dto import CloudEventDTO
from pydantic import BaseModel, Field


class CreateNotifyRequest(BaseModel):
    event: CloudEventDTO = Field(..., description="CloudEvent to publish")
