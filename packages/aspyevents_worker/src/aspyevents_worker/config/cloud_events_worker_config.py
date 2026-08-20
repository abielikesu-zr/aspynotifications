from pydantic import BaseModel, Field
from aspynats.config.cloud_events_worker_config import NatsStreamConfig


class CloudEventsWorkerConfig(BaseModel):
    """Configuration for a worker that consumes CloudEvents from JetStream."""

    name: str = Field(
        description="Unique name identifying the CloudEvents worker.",
    )
    stream: NatsStreamConfig = Field(
        default_factory=NatsStreamConfig,
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
