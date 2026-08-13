from aspypolicies.entities.aspy_policy import AspyPolicy
from pydantic import BaseModel, ConfigDict, Field


class NotificationPolicy(BaseModel):
    """
    Defines the policies used to determine whether a notification applies
    and which destinations should receive it.

    Attributes:
        id: Stable unique identifier for the notification policy.
        name: Unique or human-readable name of the notification policy.
        subject: NATS-style subject pattern used for the initial match.
        envelope_policies: Policies evaluated against the CloudEvent envelope.
        destination_policies: Policies evaluated against the full policy
            context.
        destinations: Notification destinations to use when the policy matches.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    id: str = Field(
        min_length=1,
        description="Stable unique identifier for the notification policy.",
    )

    name: str = Field(
        min_length=1,
        description="Human-readable name of the notification policy.",
    )

    subject: str = Field(
        min_length=1,
        description="NATS-style subject pattern used for the initial match.",
    )

    envelope_policies: list[AspyPolicy] = Field(
        default_factory=list,
        description="Policies evaluated against the CloudEvent envelope.",
    )

    destination_policies: list[AspyPolicy] = Field(
        default_factory=list,
        description="Policies evaluated against the full policy context.",
    )

    destinations: list[str] = Field(
        min_length=1,
        description="Destinations used when the notification policy matches.",
    )
