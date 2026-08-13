import asyncio

from aspyconfig import get_config
from aspylogger.services.logging_setup import bootstrap_logging
from aspynotifications import (
    get_destinations_service,
    get_notification_policy_service,
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

    # ---------- ensure policies exist ----------
    await ensure_policy(
        policy_service,
        name="production-node-failure",
        subject="node.*",
        envelope_policies=[
            AspyPolicy(
                name="node-error",
                expression='envelope.type == "node.error"',
                reason="The event is not a node error.",
            ),
        ],
        destination_policies=[
            AspyPolicy(
                name="production",
                expression='context.environment == "production"',
                reason="Not production.",
            ),
        ],
        destinations=["operations-email"],
    )

    await ensure_template(
        template_service,
        name="email-notification",
        template=Template(
            name="email-notification",
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
        name="slack-notification",
        template=Template(
            name="slack-notification",
            slack=SlackTemplate(
                blocks=TemplateSource(
                    file="var/notification-templates/slack-notification.yaml",
                ),
            ),
        ),
    )

    await ensure_destination(
        destinations_service,
        name="operations-email",
        provider="smtp",
        destination_type="email",
        template="email-notification",
        routable=True,
        config={
            "type": "email",
            "to": ["operations@example.com"],
        },
    )

    await ensure_destination(
        destinations_service,
        name="payments-slack",
        provider="slack",
        destination_type="slack_channel",
        template="slack-notification",
        routable=True,
        config={
            "type": "slack_channel",
            "channel_id": "payments",
        },
    )
    await ensure_policy(
        policy_service,
        name="payments-alerts",
        subject="service.payments.>",
        envelope_policies=[],
        destination_policies=[],
        destinations=["payments-slack"],
    )

    # ---------- minimal events ----------
    events = [
        {
            "name": "Unrelated service",
            "event": {
                "id": "evt-1",
                "source": "test",
                "type": "node.error",
                "subject": "service.hr.failed",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Node restarted (wrong type)",
            "event": {
                "id": "evt-2",
                "source": "test",
                "type": "node.restarted",
                "subject": "node.123",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Node failure in production",
            "event": {
                "id": "evt-3",
                "source": "test",
                "type": "node.error",
                "subject": "node.123",
                "time": "2026-08-13T10:00:00Z",
                "data": {"context": {"environment": "production"}},
            },
        },
        {
            "name": "Payments deep event",
            "event": {
                "id": "evt-4",
                "source": "test",
                "type": "payment.failed",
                "subject": "service.payments.tx.999.failed",
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

                result = renderer_service.render(
                    destination=destination,
                    template=template,
                    context=context,  # ← just pass the event
                )
                print(f"  Rendered → {destination.provider} ({destination.name})")


if __name__ == "__main__":
    asyncio.run(main())
