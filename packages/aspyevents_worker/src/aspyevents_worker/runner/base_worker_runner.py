from __future__ import annotations

import asyncio
import signal
import ssl
from collections.abc import Callable
from types import FrameType

import structlog
from aspyconfig import get_config as aspy_get_config
from aspyconfig.utils.os_utils import get_os_username
from aspylogger.services.logging_setup import configure_logging
from aspynats.config.nats_client_config import NatsClientConfig
from aspynats.config.nats_connection_config import NatsConnectionConfig
from aspynats.workers.manager_worker import ensure_stream
from nats import connect
from nats.aio.client import Client
from nats.js import JetStreamContext
from pydantic import ValidationError

from aspyevents_worker.workers.cloud_events_worker import CloudEventsWorker

logger = structlog.get_logger(__name__)


WorkerFactory = Callable[[], CloudEventsWorker]


class BaseWorkerRunner:
    """
    Base class containing the common worker startup sequence.

    Caller is responsible for calling load_config before run.

    Subclasses must define DEFAULT_CONFIG, CONFIG_ROOT and PACKAGE_NAME.
    """

    DEFAULT_CONFIG: dict = NatsClientConfig().model_dump()
    CONFIG_ROOT: str
    PACKAGE_NAME: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for attr in ("CONFIG_ROOT", "PACKAGE_NAME"):
            if not hasattr(cls, attr) or getattr(cls, attr) is None:
                raise TypeError(f"{cls.__name__} must define class attribute {attr}")

    def __init__(
        self,
        worker_factory: WorkerFactory,
    ) -> None:
        self.worker_factory = worker_factory
        self.worker: CloudEventsWorker | None = None
        self.nc: Client | None = None
        self.js: JetStreamContext | None = None

    def get_config_root(self) -> str:
        return self.CONFIG_ROOT

    def get_package_name(self) -> str:
        package_name = (self.PACKAGE_NAME or "").split(".")[0] or self.CONFIG_ROOT
        return package_name

    def get_config_path(self) -> tuple[str, str]:
        if "." in self.CONFIG_ROOT:
            config_root, config_property = self.CONFIG_ROOT.split(".", 1)
        else:
            config_root = self.CONFIG_ROOT
            config_property = "nats_client"

        return config_root, config_property

    def get_worker_config(self) -> NatsClientConfig:
        config = aspy_get_config()
        config_root, config_property = self.get_config_path()

        try:
            return config.to_pydantic(
                key=f"{config_root}.{config_property}",
                schema=NatsClientConfig,
            )
        except ValidationError as e:
            errors = "\n".join(
                f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )
            raise ValueError(f"Invalid worker configuration:\n{errors}") from e

    def load_config(
        self,
        config_file: str | None = None,
        nats_url: str | None = None,
        stream_name: str | None = None,
        stream_subject: str | None = None,
    ) -> None:
        d_config = NatsClientConfig.model_validate(
            self.DEFAULT_CONFIG,
        )

        config_root, config_property = self.get_config_path()

        app_defaults = {
            f"{config_root}": {
                f"{config_property}": d_config.model_dump(),
            }
        }

        cli_config = {
            f"{config_root}": {
                f"{config_property}": {
                    "connection": {
                        "nats_url": nats_url,
                    },
                    "stream": {
                        "name": stream_name,
                        "subject": stream_subject,
                    },
                }
            }
        }

        package_name = self.get_package_name()

        user_config_paths = [
            f"monoconfig/default/{package_name}",
        ]

        if config_file:
            user_config_paths.append(config_file)

        local_config_paths = []

        local_config_name = get_os_username()

        if local_config_name:
            local_config_paths.append(f"monoconfig/{local_config_name}/{package_name}")

        config = aspy_get_config()

        config.register_common_config(
            cli_config=cli_config,
            app_defaults=app_defaults,
            user_config_paths=user_config_paths,
            local_config_paths=local_config_paths,
        )

        config.load()

    def before_start(self) -> None:
        pass

    def before_shutdown(self) -> None:
        pass

    def handle_shutdown(
        self,
        signum: int,
        frame: FrameType | None,
    ) -> None:
        logger.debug(
            "Received shutdown signal",
            signal=signum,
        )

        self.before_shutdown()

        if self._loop.is_running() and not self._stop.done():
            self._loop.call_soon_threadsafe(
                self._stop.set_result,
                None,
            )

        logger.debug("Handle shutdown signal completed")

    def _create_ssl_context(
        self,
        config: NatsConnectionConfig,
    ) -> ssl.SSLContext | None:
        if not any(
            (
                config.tls_ca_file,
                config.tls_cert_file,
                config.tls_key_file,
            )
        ):
            return None

        ssl_context = ssl.create_default_context(
            cafile=config.tls_ca_file,
        )

        if config.tls_cert_file or config.tls_key_file:
            if not config.tls_cert_file or not config.tls_key_file:
                raise ValueError(
                    "Both tls_cert_file and tls_key_file must be configured "
                    "when using a client certificate."
                )

            ssl_context.load_cert_chain(
                certfile=config.tls_cert_file,
                keyfile=config.tls_key_file,
            )

        return ssl_context

    async def run(self) -> None:
        config = aspy_get_config()

        if not config.is_frozen():
            raise RuntimeError("Config is not loaded. Call load_config() before run().")

        configure_logging()
        worker_config = self.get_worker_config()

        self.before_start()

        # Configuration is loaded before the factory is invoked.
        self.worker = self.worker_factory()

        logger.info(
            "Worker created",
            worker=self.worker.name,
        )

        ssl_context = self._create_ssl_context(worker_config.connection)

        self.nc = await connect(
            worker_config.connection.nats_url,
            user=worker_config.connection.username,
            password=worker_config.connection.password,
            tls=ssl_context,
        )

        self.js = self.nc.jetstream()

        await ensure_stream(js=self.js, config=worker_config.stream)

        logger.info(
            "NATS JetStream connection established",
            worker=self.worker.name,
        )

        self._loop = asyncio.get_running_loop()
        self._stop = self._loop.create_future()

        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

        worker_task = asyncio.create_task(
            self.worker.run(self.js, stream_config=worker_config.stream),
            name=f"{self.worker.name}-worker",
        )

        logger.info(
            "Starting worker",
            worker=self.worker.name,
        )

        try:
            await self._stop

        finally:
            logger.info(
                "Stopping worker",
                worker=self.worker.name,
            )

            worker_task.cancel()

            await asyncio.gather(
                worker_task,
                return_exceptions=True,
            )

            if self.nc is not None:
                await self.nc.drain()
                await self.nc.close()

            logger.info("Worker stopped")
