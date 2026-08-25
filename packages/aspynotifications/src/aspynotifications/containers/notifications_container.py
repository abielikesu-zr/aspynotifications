from aspyadapters.adapters.http_client import AspyHttpClient
from aspyevents_dtos.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspyplugs.z_plug_resolver import PluginDependencyResolver
from aspypolicies import get_policy_service
from dependency_injector import containers, providers

from aspynotifications.factories.destinations_store_factory import (
    create_destinations_store,
)
from aspynotifications.factories.notification_provider_sender_factory import (
    NotificationProviderSenderFactory,
)
from aspynotifications.factories.notification_renderer_factory import (
    NotificationRendererFactory,
)
from aspynotifications.factories.policy_factory import create_notification_policy_store
from aspynotifications.factories.provider_store_factory import (
    create_notification_provider_store,
)
from aspynotifications.factories.template_store_factory import create_template_store
from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.services.admin_url_generator import AdminUrlGenerator
from aspynotifications.services.destinations_service import DestinationsService
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)
from aspynotifications.services.notifications_facade_impl import NotificationsFacadeImpl
from aspynotifications.services.notify_renderer import NotificationTemplateRenderer
from aspynotifications.services.policy_service import NotificationPolicyService
from aspynotifications.services.subject_trie import SubjectTrie
from aspynotifications.services.template_service import TemplateService


class AspyNotifictionsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # --- 1. Infrastructure / Stores ---

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

    admin_url_generator = providers.Singleton(
        AdminUrlGenerator,
        config=config.aspynotifications.admin_url_generator,
    )

    notification_provider_store = providers.Singleton(
        create_notification_provider_store,
        config=config.aspynotifications.notification_provider_store,
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

    notification_sender_http_client = providers.Singleton(
        AspyHttpClient,
        config=config.aspynotifications.notification_sender_http_client,
    )

    provider_sender_resolver = providers.Singleton(
        PluginDependencyResolver,
        dependencies=providers.Dict(
            {
                AspyHttpClient: notification_sender_http_client,
            }
        ),
    )

    notification_provider_sender_factory = providers.Singleton(
        NotificationProviderSenderFactory, resolver=provider_sender_resolver
    )

    template_renderer = providers.Singleton(
        Jinja2TemplateRenderer,
        template_root=config.aspynotifications.template_renderer.template_root,
    )

    notification_renderer_resolver = providers.Singleton(
        PluginDependencyResolver,
        dependencies=providers.Dict(
            {
                Jinja2TemplateRenderer: template_renderer,
            }
        ),
    )

    notification_renderer_factory = providers.Singleton(
        NotificationRendererFactory,
        resolver=notification_renderer_resolver,
    )

    notification_provider_service = providers.Singleton(
        NotificationProviderService,
        notification_provider_store=notification_provider_store,
        config=config.aspynotifications.notification_provider_service,
        sender_factory=notification_provider_sender_factory,
    )
    notification_policy_service = providers.Singleton(
        NotificationPolicyService,
        policy_service=policy_service,
        context_transformer=context_transformer,
        notification_policy_store=notification_policy_store,
        subject_trie=subject_trie,
        config=config.aspynotifications.policy_service,
    )
    notification_template_renderer = providers.Singleton(
        NotificationTemplateRenderer,
        admin_url_generator=admin_url_generator,
        renderer_factory=notification_renderer_factory,
    )

    notifications_facade = providers.Singleton(
        NotificationsFacadeImpl,
        template_service=template_service,
        destinations_service=destinations_service,
        notification_provider_service=notification_provider_service,
        notification_policy_service=notification_policy_service,
        notification_template_renderer=notification_template_renderer,
        config=config.aspynotifications.notification_facade,
    )
