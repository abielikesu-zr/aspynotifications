from typing import Any
from uuid import uuid4

import structlog
from aspypolicies.entities.eval_result import PolicyEvaluationResult
from aspypolicies.services.policy_service import PolicyService

from aspynotifications.adapters.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspynotifications.config.notification_config import NotificationPolicyServiceConfig
from aspynotifications.entities.notification_policy import NotificationPolicy
from aspynotifications.ports.policies_store import NotificationPolicyStore

logger = structlog.get_logger(__name__)


class NotificationPolicyService:
    """
    Domain service for the NotificationPolicy lifecycle.

    Handles notification policy CRUD operations and delegates persistence
    to the NotificationPolicyStore port.
    """

    def __init__(
        self,
        notification_policy_store: NotificationPolicyStore,
        config: dict[str, Any],
        policy_service: PolicyService,
        context_transformer: CloudEventPolicyContextTransformer,
    ):
        self.notification_policy_store = notification_policy_store
        self.config = NotificationPolicyServiceConfig.model_validate(config)
        self.policy_service = policy_service
        self.context_transformer = context_transformer

        logger.debug("NotificationPolicyService initialized")

    async def ping(self) -> bool:
        """
        Verifies that the underlying notification policy storage is healthy.
        """
        return await self.notification_policy_store.ping()

    async def create_notification_policy(
        self,
        name: str,
        subject: str,
        envelope_policies: list,
        destination_policies: list,
        destinations: list[str],
    ) -> NotificationPolicy:
        """
        Creates a new notification policy.
        """
        policy = NotificationPolicy(
            id=str(uuid4()),
            name=name,
            subject=subject,
            envelope_policies=envelope_policies,
            destination_policies=destination_policies,
            destinations=destinations,
        )

        await self.notification_policy_store.save_notification_policy(policy)

        logger.info(
            "Notification policy created",
            policy_id=policy.id,
            name=policy.name,
        )

        return policy

    async def get_notification_policy(
        self,
        policy_id: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by ID.
        """
        policy = await self.notification_policy_store.get_notification_policy_by_id(
            policy_id
        )

        if not policy:
            logger.warning(
                "Notification policy not found",
                policy_id=policy_id,
            )

        return policy

    async def get_notification_policy_by_name(
        self,
        name: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by name.
        """
        policy = await self.notification_policy_store.get_notification_policy_by_name(
            name
        )

        if not policy:
            logger.warning(
                "Notification policy not found",
                name=name,
            )

        return policy

    async def update_notification_policy(
        self,
        policy_id: str,
        name: str | None = None,
        subject: str | None = None,
        envelope_policies: list | None = None,
        destination_policies: list | None = None,
        destinations: list[str] | None = None,
    ) -> NotificationPolicy:
        """
        Updates an existing notification policy.
        """
        policy = await self._get_notification_policy_or_raise(policy_id)

        if name is not None:
            policy.name = name

        if subject is not None:
            policy.subject = subject

        if envelope_policies is not None:
            policy.envelope_policies = envelope_policies

        if destination_policies is not None:
            policy.destination_policies = destination_policies

        if destinations is not None:
            policy.destinations = destinations

        await self.notification_policy_store.save_notification_policy(policy)

        logger.info(
            "Notification policy updated",
            policy_id=policy.id,
            name=policy.name,
        )

        return policy

    async def delete_notification_policy(
        self,
        policy_id: str,
    ) -> bool:
        """
        Deletes a notification policy by ID.
        """
        policy = await self.get_notification_policy(policy_id)

        if not policy:
            return False

        await self.notification_policy_store.delete_notification_policy(policy_id)

        logger.info(
            "Notification policy deleted",
            policy_id=policy_id,
            name=policy.name,
        )

        return True

    async def list_notification_policies(
        self,
    ) -> list[NotificationPolicy]:
        """
        List all notification policies.
        """
        policies = await self.notification_policy_store.list_notification_policies()

        logger.debug(
            "Listed notification policies",
            count=len(policies),
        )

        return policies

    async def _get_notification_policy_or_raise(
        self,
        policy_id: str,
    ) -> NotificationPolicy:
        """
        Retrieve a notification policy or raise if it does not exist.
        """
        policy = await self.get_notification_policy(policy_id)

        if not policy:
            raise LookupError(f"NotificationPolicy {policy_id} not found")

        return policy

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
