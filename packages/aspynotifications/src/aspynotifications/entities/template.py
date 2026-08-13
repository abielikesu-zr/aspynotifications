from typing import Optional

from pydantic import BaseModel, Field


class TemplateSource(BaseModel):
    inline: Optional[str] = Field(
        default=None,
        description="Inline template content",
    )
    file: Optional[str] = Field(
        default=None,
        description="Path to template file",
    )


class EmailTemplate(BaseModel):
    subject: Optional[TemplateSource] = Field(
        default=None,
        description="Email subject template",
    )
    html: Optional[TemplateSource] = Field(
        default=None,
        description="Email HTML template",
    )
    text: Optional[TemplateSource] = Field(
        default=None,
        description="Email text template",
    )


class SlackTemplate(BaseModel):
    blocks: Optional[TemplateSource] = Field(
        default=None,
        description="Slack blocks template",
    )


class TeamsTemplate(BaseModel):
    adaptive_card: Optional[TemplateSource] = Field(
        default=None,
        description="Teams adaptive card template",
    )


class Template(BaseModel):
    name: str = Field(
        ...,
        description="Unique logical template name",
    )
    email: Optional[EmailTemplate] = Field(
        default=None,
        description="Email template representations",
    )
    slack: Optional[SlackTemplate] = Field(
        default=None,
        description="Slack template representations",
    )
    teams: Optional[TeamsTemplate] = Field(
        default=None,
        description="Teams template representations",
    )
