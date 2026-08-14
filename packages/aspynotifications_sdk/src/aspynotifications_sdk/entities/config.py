from pydantic import BaseModel, HttpUrl

from aspyadapters.adapters.http_client_config import HttpClientConfig


class NotificationsClientConfig(BaseModel):
    base_url: HttpUrl


class NotificationsSdkParams(BaseModel):
    http_client: HttpClientConfig
    notifications_client: NotificationsClientConfig


class NotificationsSdkConfig(BaseModel):
    notifications_sdk: NotificationsSdkParams
