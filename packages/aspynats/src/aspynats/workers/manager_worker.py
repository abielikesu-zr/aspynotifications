import structlog
from nats.js import JetStreamContext

from aspynats.config.nats_stream_config import NatsStreamConfig

logger = structlog.get_logger(__name__)


async def ensure_stream(js: JetStreamContext, config: NatsStreamConfig) -> None:
    if js is None:
        raise RuntimeError("JetStream context is not initialized")

    stream_config = config

    stream_subject = stream_config.subject

    if not stream_subject.endswith(">"):
        if not stream_subject.endswith("."):
            stream_subject += "."
        stream_subject += ">"

    try:
        stream = await js.stream_info(stream_config.name)

        if stream.config.subjects != [stream_subject]:
            raise RuntimeError(
                f"JetStream stream '{stream_config.name}' already exists "
                f"with subjects {stream.config.subjects}, "
                f"expected [{stream_subject!r}]"
            )

    except Exception as exc:
        if "stream not found" not in str(exc).lower():
            raise

        await js.add_stream(
            name=stream_config.name,
            subjects=[stream_subject],
        )

        logger.info(
            "JetStream stream created",
            stream=stream_config.name,
            subject=stream_subject,
        )
