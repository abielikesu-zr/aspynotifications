import asyncio
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
from aspynotifications.services.subject_trie import SubjectTrie

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
        subject_trie: SubjectTrie,
    ):
        self.config = NotificationPolicyServiceConfig.model_validate(config)
        self.notification_policy_store = notification_policy_store
        self.policy_service = policy_service
        self.context_transformer = context_transformer
        self.subject_trie = subject_trie

        self._trie_lock = asyncio.Lock()
        self._policy_cache: dict[str, NotificationPolicy] = {}
        self._policy_cache_valid = False

        logger.debug("NotificationPolicyService initialized")

    async def _ensure_subject_trie(self) -> None:
        if self.subject_trie.valid and self._policy_cache_valid:
            return

        async with self._trie_lock:
            # Double-check after acquiring the lock
            if self.subject_trie.valid and self._policy_cache_valid:
                return

            policies = await self.notification_policy_store.list_notification_policies()

            self.subject_trie.build((policy.subject, policy.id) for policy in policies)
            self._policy_cache = {policy.id: policy for policy in policies}
            self._policy_cache_valid = True

            logger.debug(
                "Notification policy subject trie and cache built",
                policy_count=len(policies),
            )

    def _invalidate_caches(self) -> None:
        self.subject_trie.reset()
        self._policy_cache = {}
        self._policy_cache_valid = False

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
        self._invalidate_caches()
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
        # Prefer cache when warm
        if self._policy_cache_valid:
            policy = self._policy_cache.get(policy_id)
            if policy is not None:
                return policy

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
        self._invalidate_caches()
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
        self._invalidate_caches()
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
        context: dict[str, Any],
        policy: NotificationPolicy,
    ) -> PolicyEvaluationResult:
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

    def event_to_context(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        return self.context_transformer.transform(event)

    async def find_matching_policies(
        self,
        event: dict[str, Any],
    ) -> list[NotificationPolicy]:
        await self._ensure_subject_trie()

        context = self.event_to_context(event)
        subject = context["envelope"]["type"]
        policy_ids = self.subject_trie.find_matches(subject)

        if not policy_ids:
            return []

        matches: list[NotificationPolicy] = []
        for policy_id in policy_ids:
            policy = self._policy_cache.get(policy_id)
            if policy is None:
                # Fallback (should be rare while cache is valid)
                policy = await self.get_notification_policy(policy_id)
                if policy is None:
                    continue

            result = self.event_matches_policy(context, policy)
            if result.matched:
                matches.append(policy)

        return matches
