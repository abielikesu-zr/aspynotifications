from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from aspyadapters.adapters.http_client import AspyHttpClient
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_sdk.adapters.notifications_facade_client import (
    NotificationsFacadeClient,
)
from aspynotifications_sdk.containers.aspynotifications_sdk_container import (
    NotificationsSdkContainer,
)
from aspynotifications_sdk.entities.config import NotificationClientConfig
from dependency_injector import providers
from pydantic import ValidationError


@pytest.mark.parametrize(
    "method",
    [
        "notify",
        "create_notification_policy",
        "update_notification_policy",
        "update_notification_policy_by_name",
        "activate_notification_policy",
        "deactivate_notification_policy",
        "create_template",
        "update_template",
        "create_destination",
        "update_destination",
        "create_notification_provider",
        "update_notification_provider",
    ],
)
@pytest.mark.asyncio
async def test_facade_client_delegates_to_facade(method: str) -> None:
    result = object()
    facade_method = AsyncMock(return_value=result)
    facade = SimpleNamespace(**{method: facade_method})
    client = NotificationsFacadeClient(config={}, facade=facade)
    request = object()

    assert await getattr(client, method)(request) is result
    facade_method.assert_awaited_once_with(request)


def test_facade_config_does_not_require_url() -> None:
    config = NotificationClientConfig.model_validate(
        {"adapter": {"type": "FACADE", "config": {}}}
    )
    assert config.adapter.type == "FACADE"


def test_rest_config_still_requires_url() -> None:
    with pytest.raises(ValidationError):
        NotificationClientConfig.model_validate(
            {"adapter": {"type": "REST", "config": {}}}
        )
    config = NotificationClientConfig.model_validate(
        {"adapter": {"type": "REST", "config": {"base_url": "http://localhost:50011"}}}
    )
    assert config.adapter.type == "REST"


def test_adapter_type_is_required_and_unknown_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        NotificationClientConfig.model_validate(
            {"adapter": {"config": {"base_url": "http://localhost:50011"}}}
        )
    with pytest.raises(ValidationError):
        NotificationClientConfig.model_validate(
            {"adapter": {"type": "OTHER", "config": {}}}
        )


def test_dependency_resolution_is_lazy() -> None:
    facade_factory = Mock()
    http_factory = Mock()
    container = NotificationsSdkContainer()
    container.notifications_facade.override(providers.Singleton(facade_factory))
    container.http_client.override(providers.Singleton(http_factory))

    resolver = container.notification_client_resolver()
    facade_factory.assert_not_called()
    http_factory.assert_not_called()
    assert resolver.resolve(NotificationsFacade) is facade_factory.return_value
    facade_factory.assert_called_once_with()
    http_factory.assert_not_called()
    assert resolver.resolve(AspyHttpClient) is http_factory.return_value
    http_factory.assert_called_once_with()


def test_facade_client_validates_keep_and_rejects_invalid_values() -> None:
    facade = SimpleNamespace()
    client = NotificationsFacadeClient(config={"keep": "keep"}, facade=facade)
    assert client.config.keep == "keep"
    with pytest.raises(ValidationError):
        NotificationsFacadeClient(config={"keep": "invalid"}, facade=facade)
    with pytest.raises(ValidationError):
        NotificationsFacadeClient(
            config={"keep": "keep", "unexpected": True}, facade=facade
        )
