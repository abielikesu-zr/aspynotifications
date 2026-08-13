from typing import Any

from aspynotifications.containers.notifications_container import (
    AspyNotificationsContainer,
)
from aspynotifications.entities.notification_policy import NotificationPolicy
from aspypolicies.entities.aspy_policy import AspyPolicy


def main():
    node_failed_event: dict[str, Any] = {
        "id": "evt-123",
        "source": "infrastructure",
        "type": "node.error",
        "subject": "node-123",
        "time": "2026-08-13T10:00:00Z",
        "data": {
            "event": {
                "node": {
                    "status": "failed",
                    "name": "node-123",
                    "service": "payments",
                },
            },
            "error": {
                "code": "NODE_FAILURE",
                "severity": "ERROR",
            },
            "routing": {
                "priority": "high",
            },
            "context": {
                "environment": "production",
            },
        },
    }

    node_restarted_event: dict[str, Any] = {
        "id": "evt-123",
        "source": "infrastructure",
        "type": "node.restarted",
        "subject": "node-123",
        "time": "2026-08-13T10:00:00Z",
        "data": {
            "event": {
                "node": {
                    "status": "failed",
                    "name": "node-123",
                    "service": "payments",
                },
            },
            "error": {
                "code": "NODE_FAILURE",
                "severity": "ERROR",
            },
            "routing": {
                "priority": "high",
            },
            "context": {
                "environment": "production",
            },
        },
    }
    policy = NotificationPolicy(
        name="production-node-failure",
        envelope_policies=[
            AspyPolicy(
                name="node-error",
                expression='envelope.type == "node.error"',
                reason="The event is not a node error.",
            ),
        ],
        destination_policies=[
            AspyPolicy(
                name="service-node-failed",
                expression="""
                event.node.service in ["payments", "hr"]
                and event.node.status == "failed"
            """,
                reason="A managed service node has not failed.",
            ),
            AspyPolicy(
                name="production",
                expression='context.environment == "production"',
                reason="The event is not from the production environment.",
            ),
        ],
        destinations=[
            "operations-email",
            "direct-user-email",
        ],
    )

    container = AspyNotificationsContainer()

    matcher = container.notification_policy_service()

    events = [
        (
            "Node failure",
            node_failed_event,
        ),
        (
            "Node restarted",
            node_restarted_event,
        ),
    ]

    for event_name, event in events:
        print()
        print("=" * 60)
        print(f"Testing: {event_name}")
        print("=" * 60)

        result = matcher.event_matches_policy(
            event=event,
            policy=policy,
        )

        if result.matched:
            print("✓ MATCH")
            print(f"Policy: {policy.name}")
            print("Destinations:")

            for destination in policy.destinations:
                print(f"  - {destination}")
        else:
            print("✗ NO MATCH")
            print(f"Policy: {policy.name}")
            print(f"Failed policy: {result.policy_name}")
            print(f"Reason: {result.reason}")
            print(f"Evaluated: {result.expression}")


# python notify_test.py
if __name__ == "__main__":
    main()
