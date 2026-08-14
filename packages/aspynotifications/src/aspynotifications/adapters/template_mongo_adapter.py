from typing import List

import structlog
from pydantic import BaseModel, ValidationError

from aspyadapters.adapters.generic_mongo_db_adapter import (
    GenericMongoAdapter,
    NotFoundError,
)
from aspyplugs.registry import register_plugin
from aspynotifications.entities.template import Template
from aspynotifications.ports.template_port import ITemplateStorePort

logger = structlog.get_logger(__name__)


@register_plugin("template_store", "MONGODB")
class TemplateMongoStoreAdapter(ITemplateStorePort, GenericMongoAdapter):

    def get_model_class(self) -> type[BaseModel]:   # type: ignore[override]
        return Template

    def get_collection_name(self) -> str:
        return "templates"

    async def save_template(self, template: Template) -> None:
        try:
            await self.save(template.name, template)
        except Exception as e:
            logger.error(
                "Persistence error saving template to Mongo",
                name=template.name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def get_template(self, name: str) -> Template | None:
        try:
            return await self.load(name)
        except NotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted template data found in Mongo",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def list_templates(self) -> List[Template]:
        try:
            return await self.find()
        except Exception as e:
            logger.error(
                "Persistence error listing templates",
                error=str(e),
                exc_info=e,
            )
            raise Exception(f"Error listing templates: {str(e)}") from e

    async def delete_template(self, name: str) -> None:
        try:
            await self.delete(name)
        except Exception as e:
            logger.error(
                "Persistence error deleting template from Mongo",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def ping(self) -> bool:
        try:
            return await self.ping_resource()
        except Exception as e:
            logger.error("PING error", error=str(e), exc_info=e)
            return False
