import abc
import asyncio

import structlog
from aspyevents_dtos.cloud_event_dto import CloudEventDTO
from aspynats.config.nats_stream_config import NatsStreamConfig
from aspytracing import SpanType, get_tracing
from nats import errors
from nats.js import JetStreamContext
from nats.js.api import AckPolicy, ConsumerConfig

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
        self.subs: list[JetStreamContext.PullSubscription] = []

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

    async def run(
        self, js_context: JetStreamContext, stream_config: NatsStreamConfig
    ) -> None:
        self.js = js_context
        self.stream_config = stream_config

        ack_wait = self.config.ack_wait_seconds
        max_deliver = self.config.max_deliver

        subs = await self.get_subscriptions()
        # Append the STREAM subject
        subs = self._get_stream_subscriptions(subs)
        logger.info("Subscribing", subscriptions=subs)

        for index, subject in enumerate(subs):
            durable = f"worker-{self.name.replace(' ', '-')}-{index}"

            consumer_config = ConsumerConfig(
                durable_name=durable,
                filter_subject=subject,
                ack_policy=AckPolicy.EXPLICIT,
                ack_wait=ack_wait,
                max_deliver=max_deliver,
            )

            subscription = await self.js.pull_subscribe(
                subject,
                durable=durable,
                config=consumer_config,
            )

            self.subs.append(subscription)

            logger.info(
                "Worker subscription active",
                worker=self.name,
                subject=subject,
                durable=durable,
            )

        tasks = [
            asyncio.create_task(
                self._consume(subscription),
                name=f"{self.name}-consumer-{index}",
            )
            for index, subscription in enumerate(self.subs)
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
