from pydantic import BaseModel, ConfigDict


class TemplateSourceDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inline: str | None = None
    file: str | None = None
