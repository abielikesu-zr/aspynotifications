from aspyevents import get_events_facade
from dependency_injector import containers, providers

from aspyevents_archive.workers.event_archive_worker import EventsArchiveWorker


class ArchiveWorkerContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    events_facade = providers.Singleton(
        get_events_facade,
    )

    events_archive_worker = providers.Singleton(
        EventsArchiveWorker,
        config=config.events_archive_worker.nats_worker,
        events_facade=events_facade,
    )
