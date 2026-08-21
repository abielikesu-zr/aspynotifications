from pydantic import BaseModel, Field

from aspyevents_dtos.cloud_event_dto import CloudEventDTO


class SaveEventRequest(BaseModel):
    event: CloudEventDTO = Field(..., description="CloudEvent to notify")
