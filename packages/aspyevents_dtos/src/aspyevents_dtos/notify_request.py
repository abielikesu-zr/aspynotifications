from pydantic import BaseModel, Field

from aspyevents_dtos.cloud_event_dto import CloudEventDTO


class CreateNotifyRequest(BaseModel):
    event: CloudEventDTO = Field(..., description="CloudEvent to notify")
