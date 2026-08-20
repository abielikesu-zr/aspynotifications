from aspyevents_worker.runner.base_worker_runner import BaseWorkerRunner


class NotificationsWorkerRunner(BaseWorkerRunner):
    CONFIG_ROOT = "aspynotifications_worker.nats_client"
    PACKAGE_NAME = __package__ or "aspynotifications_worker"
