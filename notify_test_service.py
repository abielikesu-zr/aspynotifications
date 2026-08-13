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

    # ---------- exercise the full service path ----------
    for case in events:
        print()
        print("=" * 60)
        print(f"Testing: {case['name']}")
        print("=" * 60)

        event = case["event"]
        print(f"Subject: {event['subject']}")

        matches = await policy_service.find_matching_policies(event)

        if not matches:
            print("✗ NO MATCH")
            continue

        for policy in matches:
            print(f"✓ MATCH → {policy.name}")
            print(f"  Destinations: {policy.destinations}")

            destinations = await get_policy_destinations(
                destinations_service,
                policy,
            )

            for destination in destinations:
                print(f"  Destination: {destination.name}")
                print(f"  Type: {destination.type}")
                print(f"  Template: {destination.template}")
                print(f"  Provider: {destination.provider}")

                template = await template_service.get_template_by_name(
                    destination.template
                )

                if template is None:
                    print(f"  Template not found: {destination.template}")
                    continue

                print(f"  Template name: {template.name}")

                if template.email is not None:
                    print("  Email:")

                    if template.email.subject is not None:
                        source = template.email.subject
                        if source.inline is not None:
                            print(f"    subject: inline={source.inline}")
                        elif source.file is not None:
                            print(f"    subject: file={source.file}")

                    if template.email.html is not None:
                        source = template.email.html
                        if source.file is not None:
                            print(f"    html: file = {source.file}")

                    if template.email.text is not None:
                        source = template.email.text
                        if source.file is not None:
                            print(f"    text: file = {source.file}")

                if template.slack is not None:
                    print("  Slack:")

                    if template.slack.blocks is not None:
                        source = template.slack.blocks
                        if source.file is not None:
                            print(f"    blocks: file = {source.file}")

                if template.teams is not None:
                    print("  Teams:")

                    if template.teams.adaptive_card is not None:
                        source = template.teams.adaptive_card
                        if source.file is not None:
                            print(f"    adaptive_card: file = {source.file}")


if __name__ == "__main__":
    asyncio.run(main())
