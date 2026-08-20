from pydantic import BaseModel, Field


class TemplateSource(BaseModel):
    inline: str | None = Field(
        default=None,
        description="Inline template content",
    )
    file: str | None = Field(
        default=None,
        description="Path to template file",
    )
