from abc import ABC, abstractmethod

from aspynotifications.entities.cloud_event import CloudEvent


class ICloudEventStorePort(ABC):
    @abstractmethod
    async def save_cloud_event(self, cloud_event: CloudEvent) -> None:
        pass

    @abstractmethod
    async def get_cloud_event(self, event_id: str) -> CloudEvent | None:
        pass

    @abstractmethod
    async def list_cloud_events(self) -> list[CloudEvent]:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        pass
