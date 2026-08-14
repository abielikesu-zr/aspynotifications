from pydantic import BaseModel


class NotificationSubscriptionsDTO(BaseModel):
    subscriptions: list[str]
