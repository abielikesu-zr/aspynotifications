from typing import List

import structlog
from pydantic import BaseModel, ValidationError

from aspyadapters.adapters.generic_local_fs import GenericLocalFSAdapter
from aspyplugs.registry import register_plugin
from aspynotifications.entities.template import Template
from aspynotifications.ports.template_port import ITemplateStorePort

logger = structlog.get_logger(__name__)


@register_plugin("template_store", "LOCALFS")
class TemplateFileStoreAdapter(ITemplateStorePort, GenericLocalFSAdapter):

    def get_model_class(self) -> type[BaseModel]:   # type: ignore[override]
        return Template

    def get_index_declarations(self) -> dict:
        return {"name": ["name"]}

    async def save_template(self, template: Template) -> None:
        filename = f"{template.name}.json"
        try:
            await self.save(filename, template)
        except Exception as e:
            logger.error(
                "Persistence error saving template to FS",
                name=template.name,
                error=str(e),
                exc_info=e,
            )
            raise

    async def get_template(self, name: str) -> Template | None:
        filename = f"{name}.json"
        try:
            return await self.load(filename)
        except FileNotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted template data found on FS",
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
        filename = f"{name}.json"
        try:
            await self.delete(filename)
        except Exception as e:
            logger.error(
                "Persistence error deleting template from FS",
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
