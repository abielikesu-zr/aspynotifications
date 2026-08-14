import abc
import asyncio

import structlog
from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from nats.js import JetStreamContext
from nats.js.api import AckPolicy, ConsumerConfig
from opentelemetry import propagate, trace
from opentelemetry.context import Context
from opentelemetry.trace import Link, SpanKind

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
        self.subs = []

    async def run(self, js_context: JetStreamContext) -> None:
        self.js = js_context

        ack_wait = self.config.ack_wait_seconds
        max_deliver = self.config.max_deliver

        for index, subject in enumerate(self.config.in_):
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

            except Exception:
                logger.exception(
                    "Worker consumer error",
                    worker=self.name,
                )
                await asyncio.sleep(1)

    async def _process(self, message) -> None:
        try:
            cloud_event = CloudEventDTO.model_validate_json(message.data)

            remote_context = propagate.extract(
                {
                    "traceparent": cloud_event.traceparent,
                    "tracestate": cloud_event.tracestate,
                }
            )

            remote_span = trace.get_current_span(remote_context)
            remote_span_context = remote_span.get_span_context()

            links = []

            if remote_span_context.is_valid:
                links.append(Link(remote_span_context))

            tracer = trace.get_tracer(self.name)

            with tracer.start_as_current_span(
                "cloud_event.process",
                context=Context(),
                kind=SpanKind.CONSUMER,
                links=links,
            ) as span:
                span.set_attribute("messaging.system", "nats")
                span.set_attribute("messaging.destination.name", message.subject)
                span.set_attribute("cloud_events.type", cloud_event.type)
                span.set_attribute("cloud_events.source", cloud_event.source)

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
