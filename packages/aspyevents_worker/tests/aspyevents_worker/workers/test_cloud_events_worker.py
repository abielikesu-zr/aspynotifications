from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase

from nats.js.api import AckPolicy
from nats.js.errors import NotFoundError

from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig
from aspyevents_worker.workers.cloud_events_worker import CloudEventsWorker
from aspynats.config.nats_stream_config import NatsStreamConfig


class FakeJetStream:
    def __init__(self, consumers: list[SimpleNamespace]) -> None:
        self.consumers = consumers
        self.created = []
        self.deleted = []

    async def consumers_info(self, stream: str) -> list[SimpleNamespace]:
        return self.consumers

    async def consumer_info(self, stream: str, durable: str) -> SimpleNamespace:
        raise NotFoundError()

    async def add_consumer(self, stream: str, config) -> SimpleNamespace:
        self.created.append(config)
        return SimpleNamespace(name=config.durable_name, config=config)

    async def delete_consumer(self, stream: str, durable: str) -> bool:
        self.deleted.append(durable)
        return True


class TestWorker(CloudEventsWorker):
    async def handle(self, cloud_event) -> None:
        pass


class CloudEventsWorkerConsumerTests(IsolatedAsyncioTestCase):
    def _worker(self) -> TestWorker:
        worker = TestWorker(
            name="notifications_worker",
            config=CloudEventsWorkerConfig(
                name="notifications_worker",
                subscriptions=["*.created"],
            ),
        )
        worker.stream_config = NatsStreamConfig(name="EVENTS", subject="events.>")
        return worker

    def test_durable_is_unique_per_subject(self) -> None:
        worker = self._worker()

        wildcard = worker._durable_for_subject("events.*.created")
        tenant = worker._durable_for_subject("events.tenant.created")

        self.assertNotEqual(wildcard, tenant)
        self.assertIn("events-any-created", wildcard)
        self.assertIn("events-tenant-created", tenant)

    async def test_reconcile_creates_per_subject_and_removes_legacy_consumers(self) -> None:
        worker = self._worker()
        js = FakeJetStream(
            consumers=[
                SimpleNamespace(
                    name="worker-notifications_worker-0",
                    config=SimpleNamespace(filter_subject="events.*.created"),
                ),
                SimpleNamespace(
                    name="unrelated-worker-0",
                    config=SimpleNamespace(filter_subject="events.other.created"),
                ),
            ]
        )
        worker.js = js

        consumers = await worker._reconcile_consumers(
            ["events.*.created", "events.tenant.created"]
        )

        self.assertEqual(js.deleted, ["worker-notifications_worker-0"])
        self.assertEqual(len(js.created), 2)
        self.assertTrue(all(config.ack_policy == AckPolicy.EXPLICIT for config in js.created))
        self.assertEqual(
            {consumer.config.filter_subject for consumer in consumers.values()},
            {"events.*.created", "events.tenant.created"},
        )

    async def test_reconcile_rejects_existing_durable_with_another_filter(self) -> None:
        worker = self._worker()
        durable = worker._durable_for_subject("events.*.created")
        worker.js = FakeJetStream(
            consumers=[
                SimpleNamespace(
                    name=durable,
                    config=SimpleNamespace(filter_subject="events.tenant.created"),
                )
            ]
        )

        with self.assertRaisesRegex(ValueError, "different filter subject"):
            await worker._reconcile_consumers(["events.*.created"])

    async def test_reconcile_reuses_consumer_with_matching_filter(self) -> None:
        worker = self._worker()
        subject = "events.*.created"
        durable = worker._durable_for_subject(subject)
        existing_consumer = SimpleNamespace(
            name=durable,
            config=SimpleNamespace(filter_subject=subject),
        )
        js = FakeJetStream(consumers=[existing_consumer])
        worker.js = js

        consumers = await worker._reconcile_consumers([subject])

        self.assertEqual(consumers, {durable: existing_consumer})
        self.assertEqual(js.created, [])
        self.assertEqual(js.deleted, [])
