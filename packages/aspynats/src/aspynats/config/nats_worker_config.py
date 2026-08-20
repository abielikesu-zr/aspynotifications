from pydantic import BaseModel, Field


class NatsStreamConfig(BaseModel):
    """Configuration for the JetStream stream that stores CloudEvents."""

    name: str = Field(
        default="EVENTS",
        description="Name of the JetStream stream used to store CloudEvents.",
    )
    subject: str = Field(
        default="events.>",
        description="Subject pattern used by the stream to capture CloudEvents.",
    )
