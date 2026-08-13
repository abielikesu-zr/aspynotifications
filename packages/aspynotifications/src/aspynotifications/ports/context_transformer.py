from typing import Any, Protocol


class PolicyContextTransformerPort(Protocol):
    def transform(self, event: Any) -> dict[str, Any]: ...
