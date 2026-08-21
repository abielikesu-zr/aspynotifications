import asyncio

from aspyconfig import get_config
from aspyevents_dtos.notify_request import CreateNotifyRequest
from aspylogger.services.logging_setup import bootstrap_logging
from aspynotifications import (
    get_destinations_service,
    get_notification_facade,
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
from aspypolicies.entities.aspy_policy import AspyPolicy

from notify_test_helpers import (
    ensure_destination,
    ensure_notification_provider,
    ensure_policy,
    ensure_template,
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
        config={},
    )

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

    facade = get_notification_facade()

    for case in events:
        case["event"].setdefault("data", {}).setdefault("context", {})[
            "test_origin"
        ] = "notify_test_facade.py"

        print()
        print("=" * 60)
        print(f"Testing: {case['name']}")
        print("=" * 60)

        result = await facade.notify(
            CreateNotifyRequest.model_validate({"event": case["event"]})
        )
        print(f"Notification status → {result}")


if __name__ == "__main__":
    asyncio.run(main())
