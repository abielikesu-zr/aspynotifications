from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from aspynotifications_dtos.base_dtos import TemplateSourceDTO
from aspynotifications_dtos.noop_dtos import (
    BHoleTemplateDTO,
    OutputHoleDestinationConfigDTO,
)


class NotificationSubscriptionsDTO(BaseModel):
    subscriptions: list[str]


class PolicyExpressionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    expression: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1)
    negative: bool = False


class CreateNotificationPolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    envelope_policies: list[PolicyExpressionDTO] = Field(default_factory=list)
    destination_policies: list[PolicyExpressionDTO] = Field(default_factory=list)
    destinations: list[str] = Field(..., min_length=1)


class UpdateNotificationPolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    envelope_policies: list[PolicyExpressionDTO] = Field(default_factory=list)
    destination_policies: list[PolicyExpressionDTO] = Field(default_factory=list)
    destinations: list[str] = Field(..., min_length=1)


class UpdateNotificationPolicyByNameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    envelope_policies: list[PolicyExpressionDTO] = Field(default_factory=list)
    destination_policies: list[PolicyExpressionDTO] = Field(default_factory=list)
    destinations: list[str] = Field(..., min_length=1)


class ActivateNotificationPolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str = Field(..., min_length=1)


class DeactivateNotificationPolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str = Field(..., min_length=1)


class NotificationPolicyDTO(CreateNotificationPolicyRequest):
    id: str = Field(..., min_length=1)
    is_active: bool


class EmailTemplateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: TemplateSourceDTO | None = None
    html: TemplateSourceDTO | None = None
    text: TemplateSourceDTO | None = None


class SlackTemplateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blocks: TemplateSourceDTO | None = None


class VSCodeTemplateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: TemplateSourceDTO
    message: TemplateSourceDTO
    severity: Literal["info", "warning", "error"] = "info"


class CreateTemplateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    email: EmailTemplateDTO | None = None
    slack: SlackTemplateDTO | None = None
    vscode: VSCodeTemplateDTO | None = None
    output_hole: BHoleTemplateDTO | None = None


class UpdateTemplateRequest(CreateTemplateRequest):
    """Full replacement request for an existing notification template."""


class TemplateDTO(CreateTemplateRequest):
    pass


class EmailDestinationConfigDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["email"] = "email"
    to: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)


class SlackChannelDestinationConfigDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["slack_channel"] = "slack_channel"


class VSCodeUserAudienceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["user"] = "user"
    recipient_user_id: str = Field(..., min_length=1)


class VSCodeGroupAudienceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["group"] = "group"
    group_id: str = Field(..., min_length=1)


class VSCodeAllAudienceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["all"] = "all"


VSCodeAudienceDTO = Annotated[
    VSCodeUserAudienceDTO | VSCodeGroupAudienceDTO | VSCodeAllAudienceDTO,
    Field(discriminator="type"),
]


class VSCodeDestinationConfigDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["vscode"] = "vscode"
    audience: VSCodeAudienceDTO


DestinationConfigDTO = Annotated[
    EmailDestinationConfigDTO
    | SlackChannelDestinationConfigDTO
    | VSCodeDestinationConfigDTO
    | OutputHoleDestinationConfigDTO,
    Field(discriminator="type"),
]


class CreateDestinationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    template: str = Field(..., min_length=1)
    config: DestinationConfigDTO


class UpdateDestinationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    template: str = Field(..., min_length=1)
    config: DestinationConfigDTO


class DestinationDTO(CreateDestinationRequest):
    id: str = Field(..., min_length=1)
    type: Literal["email", "slack_channel", "vscode", "output_hole"]
