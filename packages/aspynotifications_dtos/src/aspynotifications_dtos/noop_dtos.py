from typing import Literal

from pydantic import BaseModel, ConfigDict

from aspynotifications_dtos.base_dtos import TemplateSourceDTO


class BHoleTemplateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dumpster: TemplateSourceDTO | None = None


class OutputHoleDestinationConfigDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["output_hole"] = "output_hole"


class AHoleProviderSettingsDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str = "WARN"
    cows: bool = True


class AHoleProviderDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["SHOLE"] = "SHOLE"
    config: AHoleProviderSettingsDTO
