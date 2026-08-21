from typing import Literal

from pydantic import BaseModel, ConfigDict


class EventsFacadeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keep: Literal["keep"] = "keep"
