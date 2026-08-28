from typing import Any


class CloudEventPolicyContextTransformer:
    def transform(
        self,
        cloud_event: dict[str, Any],
    ) -> dict[str, Any]:
        data = cloud_event.get("data", {})

        return {
            "envelope": {
                "id": cloud_event.get("id"),
                "source": cloud_event.get("source"),
                "type": cloud_event.get("type"),
                "subject": cloud_event.get("subject"),
                "time": cloud_event.get("time"),
                "severity": cloud_event.get("severity") or data.get("severity"),
                "traceparent": cloud_event.get("traceparent"),
                "tracestate": cloud_event.get("tracestate"),
            },
            "event": data.get("event", {}),
            "error": data.get("error", {}),
            "routing": data.get("routing", {}),
            "context": data.get("context", {}),
        }
