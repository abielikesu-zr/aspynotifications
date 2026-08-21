from typing import Literal

from pydantic import BaseModel, ConfigDict


class CloudEventServiceConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    keep: Literal["yes"] = "yes"
