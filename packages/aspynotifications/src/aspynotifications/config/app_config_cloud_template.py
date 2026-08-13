from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig


class CloudEventServiceConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    keep: Literal["yes"] = "yes"

class CloudEventConfigParams(BaseModel):
    cloud_event_store: StorageAdapterConfig
    cloud_event_service: CloudEventServiceConfig


class TemplateServiceConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    keep: Literal["yes"] = "yes"


class TemplateConfigParams(BaseModel):
    template_store: StorageAdapterConfig
    template_service: TemplateServiceConfig


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    cloud_event: CloudEventConfigParams
    template: TemplateConfigParams
