from pydantic import BaseModel, Field

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
    output_hole: WholeTemplate | None = Field(
        default=None,
        description="Output hole template representation",
    )
