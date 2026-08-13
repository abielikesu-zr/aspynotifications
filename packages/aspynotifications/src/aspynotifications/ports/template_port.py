from abc import ABC, abstractmethod
from typing import List, Optional

from aspynotifications.entities.template import Template


class ITemplateStorePort(ABC):

    @abstractmethod
    async def save_template(self, template: Template) -> None:
        pass

    @abstractmethod
    async def get_template(self, name: str) -> Optional[Template]:
        pass

    @abstractmethod
    async def list_templates(self) -> List[Template]:
        pass

    @abstractmethod
    async def delete_template(self, name: str) -> None:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        pass
