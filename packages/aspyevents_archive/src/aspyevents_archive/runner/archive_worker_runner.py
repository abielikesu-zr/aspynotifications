from aspyevents_worker.runner.base_worker_runner import BaseWorkerRunner


class ArchiveWorkerRunner(BaseWorkerRunner):
    CONFIG_ROOT = "events_archive_worker.nats_client"
    PACKAGE_NAME = __package__ or "aspyevents_archive"
