import structlog

from aspynotifications.config.cloud_template import TemplateServiceConfig
from aspynotifications.entities.template import Template
from aspynotifications.ports.template_port import ITemplateStorePort

logger = structlog.get_logger(__name__)


class TemplateService:
    def __init__(self, config: dict, store: ITemplateStorePort):
        self._config = TemplateServiceConfig.model_validate(config)
        self._store = store

    async def create_template(self, template: Template) -> Template:
        log = logger.bind(function="create_template")
        try:
            await self._store.save_template(template)

            log.debug("Template created", name=template.name)
            return template

        except Exception as e:
            log.error(
                "Failed to create template",
                name=template.name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def update_template(self, template: Template) -> Template:
        log = logger.bind(function="update_template")
        try:
            existing_template = await self.get_template_by_name(template.name)
            if existing_template is None:
                raise ValueError(f"Template not found: {template.name}")

            await self._store.save_template(template)

            log.debug("Template updated", name=template.name)
            return template

        except Exception as e:
            log.error(
                "Failed to update template",
                name=template.name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def get_template_by_name(self, name: str) -> Template | None:
        log = logger.bind(function="get_template_by_name")
        try:
            template = await self._store.get_template(name)

            if template:
                log.debug("Template found", name=name)
            else:
                log.debug("Template not found", name=name)

            return template

        except Exception as e:
            log.error(
                "Failed to get template",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def list_templates(self) -> list[Template]:
        log = logger.bind(function="list_templates")
        try:
            templates = await self._store.list_templates()

            log.debug("Templates listed", count=len(templates))
            return templates

        except Exception as e:
            log.error(
                "Failed to list templates",
                error=str(e),
                exc_info=e,
            )
            raise

    async def delete_template(self, name: str) -> None:
        log = logger.bind(function="delete_template")
        try:
            await self._store.delete_template(name)

            log.debug("Template deleted", name=name)

        except Exception as e:
            log.error(
                "Failed to delete template",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def ping(self) -> bool:
        log = logger.bind(function="ping")
        try:
            ping_resource = await self._store.ping()

            log.debug("Ping store", ping_resource=ping_resource)
            return ping_resource

        except Exception as e:
            log.error(
                "Failed to ping",
                error=str(e),
                exc_info=e,
            )
            raise
