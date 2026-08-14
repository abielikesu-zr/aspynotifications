from pydantic import BaseModel, Field


class CloudEventsStreamConfig(BaseModel):
    name: str = "EVENTS"
    subject: str = "events.>"

    # retention: str = "limits"
    # storage: str = "file"
    # discard: str = "old"

    # max_age_seconds: float = Field(default=0, ge=0)
    # max_bytes: int = Field(default=-1)
    # max_messages: int = Field(default=-1)

    # replicas: int = Field(default=1, gt=0)

    # duplicate_window_seconds: float = Field(default=120, ge=0)


class CloudEventsWorkerConfig(BaseModel):
    name: str
    stream: CloudEventsStreamConfig = Field(default_factory=CloudEventsStreamConfig)
    subscriptions: list[str]

    batch: int = Field(default=1, gt=0)
    ack_wait_seconds: float = Field(default=300, gt=0)
    max_deliver: int = Field(default=2, gt=0)

    model_config = {
        "populate_by_name": True,
    }
