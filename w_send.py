import asyncio
import json
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:50011/api/v1"


async def post_json(
    client: httpx.AsyncClient,
    endpoint: str,
    filename: str,
) -> None:
    path = Path("var/events") / filename

    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    response = await client.post(
        f"{BASE_URL}/{endpoint}",
        json=payload,
    )

    try:
        response.raise_for_status()
        print(response.json())
    except httpx.HTTPStatusError:
        if response.status_code == 409:
            print(f"Already exists: {filename}")
            return
        raise


async def main() -> None:
    async with httpx.AsyncClient() as client:
        await post_json(
            client,
            "providers",
            "provider_ahole.json",
        )

        await post_json(
            client,
            "templates",
            "template_deep.json",
        )

        await post_json(
            client,
            "destinations",
            "destination_output_hole.json",
        )

        await post_json(
            client,
            "policies",
            "policy_excuse_created.json",
        )


if __name__ == "__main__":
    asyncio.run(main())
