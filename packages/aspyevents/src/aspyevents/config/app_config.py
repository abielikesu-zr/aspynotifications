from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from pydantic import BaseModel, ConfigDict, Field

from aspyevents.config.cloud_events_service import CloudEventServiceConfig
from aspyevents.config.events_facade_config import EventsFacadeConfig


class AspyEventsAppParams(BaseModel):
    cloud_event_store: StorageAdapterConfig
    cloud_event_service: CloudEventServiceConfig

    events_facade: EventsFacadeConfig = Field(default_factory=EventsFacadeConfig)


class AspyEventsAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspyevents: AspyEventsAppParams
