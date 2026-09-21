"""Publica una notificación de prueba en el servidor SSE POC."""

import argparse
import json
from urllib.request import Request, urlopen


def main() -> None:
    parser = argparse.ArgumentParser(description="Publica una notificación en el POC SSE.")
    parser.add_argument("--title", required=True, help="Título que mostrará VS Code.")
    parser.add_argument("--message", required=True, help="Mensaje que mostrará VS Code.")
    parser.add_argument("--user-id", required=True, help="Usuario destinatario de la notificación.")
    parser.add_argument("--severity", choices=("info", "warning", "error"), default="info")
    parser.add_argument("--url", default="http://127.0.0.1:8000/notifications")
    arguments = parser.parse_args()

    payload = json.dumps(
        {
            "title": arguments.title,
            "message": arguments.message,
            "severity": arguments.severity,
            "recipient_user_id": arguments.user_id,
        }
    ).encode("utf-8")
    request = Request(
        arguments.url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        print(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()
