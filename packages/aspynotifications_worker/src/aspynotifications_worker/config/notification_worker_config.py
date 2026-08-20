from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig
from aspynats.config.nats_client_config import NatsClientConfig
from pydantic import BaseModel, ConfigDict


class AspynotificationsWorkerParams(BaseModel):
    nats_worker: CloudEventsWorkerConfig
    nats_client: NatsClientConfig


class AspynotificationsWorkerAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspynotifications_worker: AspynotificationsWorkerParams
