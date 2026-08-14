import asyncio
import os

from aspyconfig import get_config
from aspylogger.services.logging_setup import bootstrap_logging
from aspynotifications import (
    get_destinations_service,
    get_notification_policy_service,
    get_notification_provider_service,
    get_template_service,
)
from aspynotifications.entities.template import (
    EmailTemplate,
    SlackTemplate,
    Template,
    TemplateSource,
)
from aspynotifications.services.notify_renderer import NotificationTemplateRenderer
from aspypolicies.entities.aspy_policy import AspyPolicy

from notify_test_helpers import (
    ensure_destination,
    ensure_notification_provider,
    ensure_policy,
    ensure_template,
    get_policy_destinations,
)


async def main() -> None:
    bootstrap_logging(verbose=0)
    config = get_config()
    config.register_files("mono", ["monoconfig/default"])
    config.load()

    policy_service = get_notification_policy_service()
    destinations_service = get_destinations_service()
    template_service = get_template_service()
    notification_provider_service = get_notification_provider_service()

    await ensure_notification_provider(
        notification_provider_service,
        name="corporate-mail",
        provider_type="ZEPTOMAIL",
        config={
            "from_address": "notifications@example.com",
            "from_name": "Notifications",
            "credentials": {
                "send_mail_token": "XXXXX",
            },
        },
    )

    await ensure_notification_provider(
        notification_provider_service,
        name="operations-slack",
        provider_type="SLACK",
        config={
            "webhook_url": "XXX",
        },
    )

    # ---------- ensure policies exist ----------
    await ensure_policy(
        policy_service,
        name="production-node-failure",
        subject="*.node.error",
        envelope_policies=[
            AspyPolicy(
                name="node-errors",
                expression="""
                    envelope.source == "infra-service"
                    and envelope.type == "infrastructure.node.error"
                """,
                reason="The event is not coming from the infra service.",
            ),
        ],
        destination_policies=[
            AspyPolicy(
                name="production",
                expression='context.environment == "production"',
                reason="Not production.",
            ),
        ],
        destinations=["operations-email-destination", "operations-slack-destination"],
    )

    await ensure_template(
        template_service,
        name="email-notification-template",
        template=Template(
            name="email-notification-template",
            email=EmailTemplate(
                subject=TemplateSource(
                    inline="Notification: {{ envelope.type }} — {{ envelope.subject }}",
                ),
                text=TemplateSource(
                    file="var/notification-templates/email-notification.txt",
                ),
                html=TemplateSource(
                    file="var/notification-templates/email-notification.html",
                ),
            ),
        ),
    )

    await ensure_template(
        template_service,
        name="slack-notification-template",
        template=Template(
            name="slack-notification-template",
            slack=SlackTemplate(
                blocks=TemplateSource(
                    file="var/notification-templates/slack-notification.yaml",
                ),
            ),
        ),
    )

    await ensure_destination(
        destinations_service,
        name="operations-email-destination",
        provider="corporate-mail",
        destination_type="email",
        template="email-notification-template",
        routable=True,
        config={
            "type": "email",
            "to": ["operations@example.com"],
        },
    )

    await ensure_destination(
        destinations_service,
        name="operations-slack-destination",
        provider="operations-slack",
        destination_type="slack_channel",
        template="slack-notification-template",
        routable=True,
        config={
            "type": "slack_channel",
            "channel_id": "xx",
        },
    )

    # ---------- minimal events ----------
    events = [
        {
            "name": "Unrelated service",
            "event": {
                "id": "evt-1",
                "source": "hr-service",
                "type": "infrastructure.service.failed",
                "subject": "service/hr",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Node restarted (wrong type)",
            "event": {
                "id": "evt-2",
                "source": "infra-service",
                "type": "infrastructure.node.restarted",
                "subject": "node/123",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Node failure in production",
            "event": {
                "id": "evt-3",
                "source": "infra-service",
                "type": "infrastructure.node.error",
                "subject": "node/123",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Node failure in production - dummy",
            "event": {
                "id": "evt-3d",
                "source": "dummy-service",
                "type": "infrastructure.node.error",
                "subject": "node/123",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Node failure in dev",
            "event": {
                "id": "evt-3d-dev",
                "source": "infra-service",
                "type": "infrastructure.node.error",
                "subject": "node/123",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "dev"}},
            },
        },
        {
            "name": "Node failure in production",
            "event": {
                "id": "evt-www3",
                "source": "infra-service",
                "type": "infrastructure.node.error",
                "subject": "node/456",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Payments deep event",
            "event": {
                "id": "evt-4",
                "source": "payments-service",
                "type": "payments.payment.failed",
                "subject": "payment/999",
                "time": "2026-08-13T10:00:00Z",
                "data": {},
            },
        },
    ]

    renderer_service = NotificationTemplateRenderer(template_root=".")

    for case in events:
        print()
        print("=" * 60)
        print(f"Testing: {case['name']}")
        print("=" * 60)
        context = policy_service.event_to_context(case["event"])
        print(f"Subject: {context['envelope']['subject']}")

        matches = await policy_service.find_matching_policies(case["event"])
        if not matches:
            print("✗ NO MATCH")
            continue

        for policy in matches:
            print(f"✓ MATCH → {policy.name}")

            destinations = await get_policy_destinations(
                destinations_service,
                policy,
            )

            for destination in destinations:
                template = await template_service.get_template_by_name(
                    destination.template
                )
                if template is None:
                    print(f"  Template not found: {destination.template}")
                    continue

                rendered_message = renderer_service.render(
                    destination=destination,
                    template=template,
                    context=context,
                )

                provider = await notification_provider_service.get_notification_provider_by_name(
                    destination.provider
                )

                if provider is None:
                    print(f"  Provider not found: {destination.provider}")
                    continue

                result = await notification_provider_service.send(
                    provider=provider,
                    destination=destination,
                    message=rendered_message,
                )
                print(f"  Delivery status → {result.status}")


if __name__ == "__main__":
    asyncio.run(main())
