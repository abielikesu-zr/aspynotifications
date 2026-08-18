from pydantic import BaseModel, Field


class CloudEventsStreamConfig(BaseModel):
    """Configuration for the JetStream stream that stores CloudEvents."""

    name: str = Field(
        default="EVENTS",
        description="Name of the JetStream stream used to store CloudEvents.",
    )
    subject: str = Field(
        default="events.>",
        description="Subject pattern used by the stream to capture CloudEvents.",
    )

    # retention: str = "limits"
    # storage: str = "file"
    # discard: str = "old"

    # max_age_seconds: float = Field(default=0, ge=0)
    # max_bytes: int = Field(default=-1)
    # max_messages: int = Field(default=-1)

    # replicas: int = Field(default=1, gt=0)

    # duplicate_window_seconds: float = Field(default=120, ge=0)


class CloudEventsWorkerConfig(BaseModel):
    """Configuration for a worker that consumes CloudEvents from JetStream."""

    name: str = Field(
        description="Unique name identifying the CloudEvents worker.",
    )
    stream: CloudEventsStreamConfig = Field(
        default_factory=CloudEventsStreamConfig,
        description="JetStream stream configuration used by the worker for CloudEvents.",
    )
    subscriptions: list[str] = Field(
        description="List of NATS subjects to which the worker subscribes for CloudEvents.",
    )

    batch: int = Field(
        default=1,
        gt=0,
        description="Maximum number of CloudEvents processed in a single batch.",
    )
    ack_wait_seconds: float = Field(
        default=300,
        gt=0,
        description="Maximum time in seconds that a message may remain unacknowledged before JetStream considers it eligible for redelivery.",
    )
    max_deliver: int = Field(
        default=2,
        gt=0,
        description="Maximum number of delivery attempts allowed for a message before it is considered undeliverable.",
    )

    model_config = {
        "populate_by_name": True,
    }
