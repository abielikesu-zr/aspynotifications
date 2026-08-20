from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.entities.source import TemplateSource


class WholeTemplate(BaseModel):
    dumpster: TemplateSource | None = Field(
        default=None,
        description="Output hole template content",
    )


class OutputHoleDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["output_hole"] = "output_hole"


class AHoleProviderSettings(BaseModel):
    level: str = Field(
        default="WARN",
        description="Log level used for output",
    )
    cows: bool = Field(
        default=True,
        description="Whether cows should be included in output",
    )


class AHoleProvider(BaseModel):
    type: Literal["SHOLE"] = Field(
        "SHOLE",
        description="Type of notification provider",
    )
    config: AHoleProviderSettings = Field(
        ...,
        description="BHole-specific configuration",
    )
