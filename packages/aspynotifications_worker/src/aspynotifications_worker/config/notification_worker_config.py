from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig
from aspyevents_worker.config.nats_connection_config import NatsConnectionConfig
from pydantic import BaseModel, ConfigDict


class AspynotificationsWorkerParams(BaseModel):
    nats_worker: CloudEventsWorkerConfig
    nats_connection: NatsConnectionConfig


class AspynotificationsWorkerAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspynotifications_worker: AspynotificationsWorkerParams
