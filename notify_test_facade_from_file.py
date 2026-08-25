import argparse
import asyncio
from pathlib import Path
from typing import Any

import yaml
from aspyconfig import get_config
from aspyevents_dtos.save_event_request import CreateNotifyRequest
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


def load_cases(source_files: list[Path]) -> list[dict[str, Any]]:
    """Load notification test cases from the configured YAML files."""
    cases: list[dict[str, Any]] = []

    for source_file in source_files:
        with source_file.open(encoding="utf-8") as source:
            source_data = yaml.safe_load(source) or {}

        file_cases = source_data["cases"]
        if not isinstance(file_cases, list):
            raise ValueError(f"'cases' must be a list in {source_file}")

        cases.extend(file_cases)

    return cases


async def prepare_notification_configuration() -> None:
    """Create the fixed administrative records required by the test cases."""
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
            "credentials": {"send_mail_token": "XXXXX"},
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
                expression=(
                    'envelope.source == "infra-service"\n'
                    'and envelope.type == "infrastructure.node.error"'
                ),
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
                    inline="Notification: {{ envelope.type }} — {{ envelope.subject }}"
                ),
                text=TemplateSource(
                    file="var/notification-templates/email-notification.txt"
                ),
                html=TemplateSource(
                    file="var/notification-templates/email-notification.html"
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
                    file="var/notification-templates/slack-notification.yaml"
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
        config={"type": "email", "to": ["operations@example.com"]},
    )
    await ensure_destination(
        destinations_service,
        name="operations-slack-destination",
        provider="operations-slack",
        destination_type="slack_channel",
        template="slack-notification-template",
        config={"type": "slack_channel"},
    )


async def main(source_files: list[Path]) -> None:
    bootstrap_logging(verbose=0)
    config = get_config()
    config.register_files("mono", ["monoconfig/default"])
    config.load()

    await prepare_notification_configuration()
    facade = get_notification_facade()

    for case in load_cases(source_files):
        case["event"].setdefault("data", {}).setdefault("context", {})[
            "test_origin"
        ] = "notify_test_facade_from_file.py"

        print()
        print("=" * 60)
        print(f"Testing: {case['name']}")
        print("=" * 60)

        request = CreateNotifyRequest.model_validate({"event": case["event"]})
        result = await facade.notify(request)
        print(f"Notification status → {result}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--notification-source",
        action="append",
        type=Path,
        required=True,
        help="YAML file containing notification test cases; repeat for multiple files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    asyncio.run(main(arguments.notification_source))
