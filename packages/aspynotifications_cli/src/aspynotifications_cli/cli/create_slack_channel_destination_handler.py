import json

from aspylogger.services.logging_setup import configure_logging
from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    SlackChannelDestinationConfigDTO,
)
from aspynotifications_sdk import get_notifications_sdk

from aspynotifications_cli import load_aspynotifications_cli_config


async def create_slack_channel_destination_handler(
    name: str,
    provider: str,
    template: str,
    routable: bool,
    channel_id: str,
    output_format: str,
) -> None:
    load_aspynotifications_cli_config()
    configure_logging()
    result = await get_notifications_sdk().create_destination(
        CreateDestinationRequest(
            name=name,
            provider=provider,
            template=template,
            routable=routable,
            config=SlackChannelDestinationConfigDTO(channel_id=channel_id),
        )
    )
    data = result.model_dump(mode="json")
    if output_format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(f"Created Slack channel destination: {data['name']} ({data['id']})")
