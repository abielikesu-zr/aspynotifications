from aspypolicies import get_policy_service
from dependency_injector import containers, providers

from aspynotifications.adapters.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspynotifications.services.notification_policy_service import (
    NotificationPolicyService,
)


class AspyNotificationsContainer(containers.DeclarativeContainer):
    policy_service = providers.Singleton(
        get_policy_service,
    )

    context_transformer = providers.Singleton(
        CloudEventPolicyContextTransformer,
    )

    notification_policy_service = providers.Singleton(
        NotificationPolicyService,
        policy_service=policy_service,
        context_transformer=context_transformer,
    )
