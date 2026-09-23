from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.entities.noop import WholeTemplate
from aspynotifications.entities.source import TemplateSource


class EmailTemplate(BaseModel):
    subject: TemplateSource | None = Field(
        default=None,
        description="Email subject template",
    )
    html: TemplateSource | None = Field(
        default=None,
        description="Email HTML template",
    )
    text: TemplateSource | None = Field(
        default=None,
        description="Email text template",
    )


class SlackTemplate(BaseModel):
    blocks: TemplateSource | None = Field(
        default=None,
        description="Slack blocks template",
    )


class VSCodeTemplate(BaseModel):
    """Templates rendered into the payload consumed by the VS Code relay."""

    model_config = ConfigDict(extra="forbid")

    title: TemplateSource = Field(..., description="VS Code notification title")
    message: TemplateSource = Field(..., description="VS Code notification message")
    severity: Literal["info", "warning", "error"] = Field(default="info")


class Template(BaseModel):
    name: str = Field(
        ...,
        description="Unique logical template name",
    )
    email: EmailTemplate | None = Field(
        default=None,
        description="Email template representations",
    )
    slack: SlackTemplate | None = Field(
        default=None,
        description="Slack template representations",
    )
    vscode: VSCodeTemplate | None = Field(
        default=None,
        description="VS Code template representation",
    )
    output_hole: WholeTemplate | None = Field(
        default=None,
        description="Output hole template representation",
    )
