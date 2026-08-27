import structlog
from nats.jetstream import JetStream, StreamConfig  # type: ignore[import-untyped]

from aspynats.config.nats_stream_config import NatsStreamConfig

logger = structlog.get_logger(__name__)


async def ensure_stream(
    js: JetStream,
    config: NatsStreamConfig,
) -> None:
    stream_subject = config.subject

    if not stream_subject.endswith(">"):
        if not stream_subject.endswith("."):
            stream_subject += "."
        stream_subject += ">"

    try:
        stream = await js.get_stream(config.name)
        stream_info = stream.info

        if stream_info is None:
            raise RuntimeError(
                f"JetStream stream '{config.name}' has no stream information"
            )

        if stream_info.config.subjects != [stream_subject]:
            raise RuntimeError(
                f"JetStream stream '{config.name}' already exists "
                f"with subjects {stream_info.config.subjects}, "
                f"expected [{stream_subject!r}]"
            )

    except Exception as exc:
        if "stream not found" not in str(exc).lower():
            raise

        await js.create_stream(
            StreamConfig(
                name=config.name,
                subjects=[stream_subject],
            )
        )

        logger.info(
            "JetStream stream created",
            stream=config.name,
            subject=stream_subject,
        )
