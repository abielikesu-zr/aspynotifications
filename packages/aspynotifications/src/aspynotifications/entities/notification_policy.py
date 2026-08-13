from aspypolicies.entities.aspy_policy import AspyPolicy
from pydantic import BaseModel, ConfigDict, Field


class NotificationPolicy(BaseModel):
    """
    Defines the policies used to determine whether a notification applies
    and which destinations should receive it.

    Attributes:
        name: Unique or human-readable name of the notification policy.
        envelope_policies: Policies evaluated against the CloudEvent envelope.
        destination_policies: Policies evaluated against the full policy
            context when determining whether the notification applies.
        destinations: Notification destinations to use when the policy matches.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    name: str = Field(
        min_length=1,
        description="Unique or human-readable notification policy name.",
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
