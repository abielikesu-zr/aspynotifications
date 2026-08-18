from typing import Any, cast

from aspyadapters.adapters.http_client import AspyHttpClient
from aspyplugs.registry import register_plugin

from aspynotifications.config.destination_config import EmailDestinationConfig
from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import (
    NotificationProvider,
    ZeptoMailProvider,
)
from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)


@register_plugin("notification_sender", "ZEPTOMAIL")
class ZeptoMailNotificationSender(INotificationProviderSender):
    """ZeptoMail delivery adapter."""

    def __init__(self, http_client: AspyHttpClient) -> None:
        self._http = http_client

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        provider_config = cast(ZeptoMailProvider, provider.provider).config
        destination_config = cast(EmailDestinationConfig, destination.config)

        payload: dict[str, Any] = {
            "from": {
                "address": provider_config.from_address,
                "name": provider_config.from_name,
            },
            "to": [
                {"email_address": {"address": address}}
                for address in destination_config.to
            ],
            "cc": [
                {"email_address": {"address": address}}
                for address in destination_config.cc
            ],
            "bcc": [
                {"email_address": {"address": address}}
                for address in destination_config.bcc
            ],
            "subject": message["subject"],
        }

        if message["html"] is not None:
            payload["htmlbody"] = message["html"]
        else:
            payload["textbody"] = message["text"]

        response = await self._http.post(
            "https://api.zeptomail.com/v1.1/email",
            headers={
                "Accept": "application/json",
                "Authorization": (
                    "Zoho-enczapikey "
                    f"{provider_config.credentials.send_mail_token}"
                ),
            },
            payload=payload,
        )

        print(
            f"ZeptoMail accepted the message for provider {provider.name}: "
            f"HTTP {response.status_code}."
        )
        return DeliveryResult(
            status="accepted",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
