from aspypolicies import get_policy_service
from dependency_injector import containers, providers

from aspynotifications.adapters.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspynotifications.factories.cloud_event_store_factory import (
    create_cloud_event_store,
)
from aspynotifications.factories.destinations_store_factory import (
    create_destinations_store,
)
from aspynotifications.factories.policy_factory import create_notification_policy_store
from aspynotifications.factories.template_store_factory import create_template_store
from aspynotifications.services.cloud_event_service import CloudEventService
from aspynotifications.services.destinations_service import DestinationsService
from aspynotifications.services.policy_service import NotificationPolicyService
from aspynotifications.services.subject_trie import SubjectTrie
from aspynotifications.services.template_service import TemplateService


class AspyNotificationsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # --- 1. Infrastructure / Stores ---
    cloud_event_store = providers.Singleton(
        create_cloud_event_store,
        config=config.aspynotifications.cloud_event_store,
    )

    cloud_event_service = providers.Singleton(
        CloudEventService,
        store=cloud_event_store,
        config=config.aspynotifications.cloud_event_service,
    )

    template_store = providers.Singleton(
        create_template_store,
        config=config.aspynotifications.template_store,
    )

    template_service = providers.Singleton(
        TemplateService,
        store=template_store,
        config=config.aspynotifications.template_service,
    )

    notification_policy_store = providers.Singleton(
        create_notification_policy_store,
        config=config.aspynotifications.policy_store,
    )

    destinations_store = providers.Singleton(
        create_destinations_store,
        config=config.aspynotifications.destinations_store,
    )

    policy_service = providers.Singleton(
        get_policy_service,
    )

    context_transformer = providers.Singleton(
        CloudEventPolicyContextTransformer,
    )
    subject_trie = providers.Singleton(
        SubjectTrie,
    )
    destinations_service = providers.Singleton(
        DestinationsService,
        store=destinations_store,
        config=config.aspynotifications.destinations_service,
    )

    notification_policy_service = providers.Singleton(
        NotificationPolicyService,
        policy_service=policy_service,
        context_transformer=context_transformer,
        notification_policy_store=notification_policy_store,
        subject_trie=subject_trie,
        config=config.aspynotifications.policy_service,
    )
