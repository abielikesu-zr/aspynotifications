from typing import Literal

from pydantic import BaseModel, ConfigDict


class TemplateServiceConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    keep: Literal["yes"] = "yes"
