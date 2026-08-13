from aspyconfig import get_config
from aspylogger.services.logging_setup import bootstrap_logging
from aspynotifications import get_notification_policy_service
from aspynotifications.entities.notification_policy import NotificationPolicy
from aspynotifications.services.subject_trie import SubjectTrie
from aspypolicies.entities.aspy_policy import AspyPolicy


def main():
    bootstrap_logging(verbose=0)
    config = get_config()
    config.register_files("mono", ["monoconfig/default"])
    config.load()

    # ---------- policies ----------
    policies = [
        NotificationPolicy(
            id="pol-node-error",
            subject="node.*",
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
                    name="production",
                    expression='context.environment == "production"',
                    reason="Not production.",
                ),
            ],
            destinations=["operations-email"],
        ),
        NotificationPolicy(
            id="pol-payments",
            subject="service.payments.>",
            name="payments-alerts",
            envelope_policies=[],
            destination_policies=[],
            destinations=["payments-slack"],
        ),
    ]

    # ---------- build trie ----------
    trie = SubjectTrie()
    trie.build([(p.subject, p.id) for p in policies])
    policy_by_id = {p.id: p for p in policies}

    # ---------- minimal events ----------
    events = [
        # 1. Should be discarded by trie (no matching subject pattern)
        {
            "name": "Unrelated service",
            "event": {
                "type": "node.error",
                "subject": "service.hr.failed",
                "data": {"context": {"environment": "production"}},
            },
        },
        # 2. Passes trie (node.*), fails envelope policy
        {
            "name": "Node restarted (wrong type)",
            "event": {
                "type": "node.restarted",
                "subject": "node.123",
                "data": {"context": {"environment": "production"}},
            },
        },
        # 3. Passes trie + all policies
        {
            "name": "Node failure in production",
            "event": {
                "type": "node.error",
                "subject": "node.123",
                "data": {"context": {"environment": "production"}},
            },
        },
        # 4. Passes trie via service.payments.>
        {
            "name": "Payments deep event",
            "event": {
                "type": "payment.failed",
                "subject": "service.payments.tx.999.failed",
                "data": {},
            },
        },
    ]

    policy_service = get_notification_policy_service()

    for case in events:
        print()
        print("=" * 60)
        print(f"Testing: {case['name']}")
        print("=" * 60)

        event_data = case["event"]
        context = policy_service.event_to_context(event_data)

        subject = context["envelope"]["subject"]

        # 1. cheap subject gate
        candidate_ids = trie.find_matches(subject)
        print(f"Subject: {subject}")
        print(f"Trie candidates: {candidate_ids}")

        if not candidate_ids:
            print("✗ DISCARDED by subject trie")
            continue

        # 2. full policy checks on survivors
        any_match = False
        for pid in candidate_ids:
            policy = policy_by_id[pid]
            result = policy_service.event_matches_policy(context=context, policy=policy)

            if result.matched:
                any_match = True
                print(f"✓ MATCH → {policy.name}")
                print(f"  Destinations: {policy.destinations}")
            else:
                print(f"✗ Policy {policy.name} rejected")
                print(f"  Failed: {result.policy_name}")
                print(f"  Reason: {result.reason}")

        if not any_match:
            print("→ No policy fully matched")


if __name__ == "__main__":
    main()
