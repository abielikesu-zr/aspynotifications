from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DeliveryResult:
    """Outcome of sending a rendered notification through a provider."""

    status: Literal["accepted"]
    provider_name: str
    provider_type: str
    sender_name: str
