from typing import Any

from aspypolicies.entities.eval_result import PolicyEvaluationResult
from aspypolicies.services.policy_service import PolicyService

from aspynotifications.adapters.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspynotifications.entities.notification_policy import NotificationPolicy


class NotificationPolicyService:
    def __init__(
        self,
        policy_service: PolicyService,
        context_transformer: CloudEventPolicyContextTransformer,
    ):
        self.policy_service = policy_service
        self.context_transformer = context_transformer

    def event_matches_policy(
        self,
        event: dict[str, Any],
        policy: NotificationPolicy,
    ) -> PolicyEvaluationResult:
        context = self.context_transformer.transform(event)

        envelope_result = self.policy_service.evaluate_policies(
            policy.envelope_policies,
            context,
        )

        if not envelope_result.matched:
            return envelope_result

        return self.policy_service.evaluate_policies(
            policy.destination_policies,
            context,
        )
