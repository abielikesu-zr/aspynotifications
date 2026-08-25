import abc
import asyncio
import hashlib
import re

import structlog
from aspyevents_dtos.cloud_event_dto import CloudEventDTO
from aspynats.config.nats_stream_config import NatsStreamConfig
from aspytracing import SpanType, get_tracing
from nats import errors
from nats.js import JetStreamContext
from nats.js.api import AckPolicy, ConsumerConfig, ConsumerInfo
from nats.js.errors import NotFoundError

from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig

logger = structlog.get_logger(__name__)


class CloudEventsWorker(abc.ABC):
    def __init__(
        self,
        name: str,
        config: CloudEventsWorkerConfig,
    ) -> None:
        self.name = name
        self.config = config
        self.batch_size = config.batch
        self.js: JetStreamContext | None = None
        self.stream_config: NatsStreamConfig | None = None

    async def get_subscriptions(self) -> list[str]:
        return self.config.subscriptions

    def _get_stream_subscriptions(
        self,
        subscriptions: list[str],
    ) -> list[str]:
        stream_subject = self.stream_config.subject  # type: ignore
        if not stream_subject.endswith(">"):
            if not stream_subject.endswith("."):
                stream_subject += "."
            stream_subject += ">"

        prefix = stream_subject.removesuffix(">")

        return [
            subscription
            if subscription.startswith(prefix)
            else f"{prefix}{subscription}"
            for subscription in subscriptions
        ]

    def _durable_prefix(self) -> str:
        """Return the durable-name namespace owned by this worker."""
        return f"worker-{self.name.replace(' ', '-')}"

    def _durable_for_subject(self, subject: str) -> str:
        """Build a readable, collision-resistant durable name for a filter."""
        subject_label = subject.replace("*", "any").replace(">", "all")
        subject_label = re.sub(r"[^A-Za-z0-9_-]+", "-", subject_label).strip("-")
        subject_hash = hashlib.sha256(subject.encode()).hexdigest()[:12]
        return f"{self._durable_prefix()}-{subject_label}-{subject_hash}"

    def _is_owned_durable(self, durable: str) -> bool:
        """Whether a durable is managed by this worker, including legacy ones."""
        prefix = self._durable_prefix()
        return durable == prefix or durable.startswith(f"{prefix}-")

    async def _reconcile_consumers(self, subjects: list[str]) -> dict[str, ConsumerInfo]:
        """Create, validate, and remove consumers owned by this worker.

        A durable is tied to one filter subject.  This prevents a reordered
        subscription list from binding a previous consumer to another filter.
        """
        if self.js is None or self.stream_config is None:
            raise RuntimeError("Worker must be initialized before reconciling consumers")

        stream = self.stream_config.name
        desired = {
            self._durable_for_subject(subject): subject
            for subject in dict.fromkeys(subjects)
        }

        existing_consumers = await self.js.consumers_info(stream)
        existing_by_name = {consumer.name: consumer for consumer in existing_consumers}

        for durable, subject in desired.items():
            consumer = existing_by_name.get(durable)
            if consumer is not None and consumer.config.filter_subject != subject:
                raise ValueError(
                    "Existing worker consumer has a different filter subject "
                    f"(durable={durable!r}, expected={subject!r}, "
                    f"actual={consumer.config.filter_subject!r})"
                )

        for durable in existing_by_name:
            if self._is_owned_durable(durable) and durable not in desired:
                await self.js.delete_consumer(stream, durable)
                logger.info(
                    "Removed stale worker consumer",
                    worker=self.name,
                    durable=durable,
                )

        consumers: dict[str, ConsumerInfo] = {}
        for durable, subject in desired.items():
            consumer = existing_by_name.get(durable)
            if consumer is None:
                try:
                    consumer = await self.js.consumer_info(stream, durable)
                except NotFoundError:
                    consumer = await self.js.add_consumer(
                        stream,
                        config=ConsumerConfig(
                            durable_name=durable,
                            filter_subject=subject,
                            ack_policy=AckPolicy.EXPLICIT,
                            ack_wait=self.config.ack_wait_seconds,
                            max_deliver=self.config.max_deliver,
                        ),
                    )

            if consumer.config.filter_subject != subject:
                raise ValueError(
                    "Worker consumer filter does not match the requested subject "
                    f"(durable={durable!r}, expected={subject!r}, "
                    f"actual={consumer.config.filter_subject!r})"
                )
            consumers[durable] = consumer

        return consumers

    async def run(
        self, js_context: JetStreamContext, stream_config: NatsStreamConfig
    ) -> None:
        self.js = js_context
        self.stream_config = stream_config

        subs = await self.get_subscriptions()
        subs = self._get_stream_subscriptions(subs)

        logger.info(
            "Subscribing",
            worker=self.name,
            subscriptions=subs,
        )

        consumers = await self._reconcile_consumers(subs)
        subscriptions = []
        for durable, consumer in consumers.items():
            subscription = await self.js.pull_subscribe_bind(
                durable,
                self.stream_config.name,
            )
            subscriptions.append(subscription)
            logger.info(
                "Worker subscription active",
                worker=self.name,
                subject=consumer.config.filter_subject,
                durable=durable,
            )

        tasks = [
            asyncio.create_task(self._consume(subscription), name=f"{self.name}-{index}")
            for index, subscription in enumerate(subscriptions)
        ]
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _consume(self, subscription) -> None:
        while True:
            try:
                messages = await subscription.fetch(self.batch_size)

                for message in messages:
                    await self._process(message)

            except asyncio.CancelledError:
                raise

            except errors.TimeoutError:
                continue

            except Exception as e:
                logger.debug(
                    "Worker consumer error", worker=self.name, error=str(e), exc_info=e
                )
                await asyncio.sleep(1)

    async def _process(self, message) -> None:
        tracing = get_tracing()
        try:
            cloud_event = CloudEventDTO.model_validate_json(message.data)

            trace_context: dict[str, str | None] = {
                "traceparent": cloud_event.traceparent,
                "tracestate": cloud_event.tracestate,
            }

            with tracing.start_or_continue_trace(
                span_name="cloud_event.process",
                trace_context=trace_context,
                kind=SpanType.CONSUMER,
                attributes={
                    "messaging.system": "nats",
                    "messaging.destination.name": message.subject,
                    "cloud_events.type": cloud_event.type,
                    "cloud_events.source": cloud_event.source,
                },
            ):
                await self.handle(cloud_event)

                await message.ack()

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "CloudEvent processing failed",
                worker=self.name,
                subject=message.subject,
            )

            await message.nak(delay=1)

    @abc.abstractmethod
    async def handle(self, cloud_event: CloudEventDTO) -> None:
        """Process a CloudEvent."""
        ...
