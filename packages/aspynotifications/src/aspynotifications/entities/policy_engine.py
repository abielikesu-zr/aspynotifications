from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PolicyEngineMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    headers: dict[str, str] = Field(
        default_factory=dict,
        description="CloudEvent attributes and extension attributes to match",
    )
    event: Optional[dict[str, str]] = Field(
        default=None,
        description="Optional event or context values to match",
    )


class PolicyEngine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        min_length=1,
        description="Unique textual identifier for the policy engine",
    )
    name: str = Field(
        ...,
        min_length=1,
        description="Human-readable policy engine name",
    )
    match: PolicyEngineMatch = Field(
        ...,
        description="CloudEvent matching criteria",
    )
    destinations: list[str] = Field(
        ...,
        min_length=1,
        description="Destination names selected when the policy engine matches",
    )
