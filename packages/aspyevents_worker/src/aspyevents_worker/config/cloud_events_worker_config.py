from pydantic import BaseModel, Field


class CloudEventsWorkerConfig(BaseModel):
    in_: list[str] = Field(alias="in")
    batch: int = Field(default=1, gt=0)
    ack_wait_seconds: float = Field(default=300, gt=0)
    max_deliver: int = Field(default=2, gt=0)

    model_config = {
        "populate_by_name": True,
    }
