import hashlib
import json
import logging

import redis

from sqlalchemy.orm import Session

from app.cache.redis_client import redis_client
from app.models.environment import Environment
from app.models.flag import Flag
from app.models.targeting_rule import TargetingRule
from app.models.user_group_membership import UserGroupMembership


logger = logging.getLogger(__name__)


def _build_cache_key(
    environment_name: str,
    flag_key: str,
    user_context: dict | None = None,
) -> str:
    """
    Build a cache key that is safe for user-specific evaluations.

    Different users/contexts must not share the same cached evaluation.
    """

    context = user_context or {}

    context_json = json.dumps(
        context,
        sort_keys=True,
        separators=(",", ":"),
    )

    context_hash = hashlib.sha256(
        context_json.encode("utf-8")
    ).hexdigest()

    return f"flag:{environment_name}:{flag_key}:{context_hash}"


def _escape_redis_glob(value: str) -> str:
    """Escape a literal cache namespace component for Redis glob matching."""

    return (
        value.replace("\\", "\\\\")
        .replace("*", "\\*")
        .replace("?", "\\?")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def invalidate_flag_cache(environment_name: str, flag_key: str) -> int:
    """Remove every context-specific evaluation cache entry for one flag.

    Evaluation keys include a hash of the user context, so deleting a single
    exact key cannot invalidate all decisions for a flag. ``scan_iter`` keeps
    the operation incremental and avoids Redis' blocking ``KEYS`` command.
    """

    pattern = (
        f"flag:{_escape_redis_glob(environment_name)}:"
        f"{_escape_redis_glob(flag_key)}:*"
    )
    deleted = 0
    batch: list[str] = []

    for cache_key in redis_client.scan_iter(match=pattern, count=100):
        batch.append(cache_key)
        if len(batch) == 100:
            deleted += redis_client.delete(*batch)
            batch.clear()

    if batch:
        deleted += redis_client.delete(*batch)

    return deleted


def invalidate_flag_cache_safely(environment_name: str, flag_key: str) -> int | None:
    """Best-effort invalidation after a committed database mutation.

    Redis is an optimization; an unavailable cache must not turn a committed
    PostgreSQL mutation into an API failure. Cached evaluations can remain
    stale until Redis recovers and a later invalidation or expiry removes them.
    """

    try:
        return invalidate_flag_cache(environment_name, flag_key)
    except (redis.exceptions.RedisError, OSError) as exc:
        logger.warning(
            "Redis cache invalidation skipped for %s/%s; cached evaluations may remain stale: %s",
            environment_name,
            flag_key,
            exc,
        )
        return None


def _cache_result(
    cache_key: str,
    result: dict,
) -> None:
    """
    Store the complete evaluation result in Redis.
    """

    redis_client.set(
        cache_key,
        json.dumps(result),
    )


def _get_cached_result(cache_key: str):
    """
    Retrieve a complete evaluation result from Redis.
    """

    cached_value = redis_client.get(cache_key)

    if not cached_value:
        return None

    try:
        return json.loads(cached_value)
    except (json.JSONDecodeError, TypeError):
        return None


def evaluate_flag(
    db: Session,
    flag_key: str,
    environment_name: str,
    user_context: dict | None = None,
):
    """
    Evaluate a feature flag for a given environment and user context.

    Evaluation order:

    1. Environment
    2. Flag
    3. Redis cache
    4. User targeting
    5. Group targeting
    6. Percentage rollout
    7. Default flag state
    """

    user_context = user_context or {}

    # 1. Find Environment

    environment = (
        db.query(Environment)
        .filter(Environment.name == environment_name)
        .first()
    )

    if environment is None:
        return {
            "success": False,
            "message": "Environment not found",
        }

    # 2. Find Flag

    flag = (
        db.query(Flag)
        .filter(
            Flag.key == flag_key,
            Flag.environment_id == environment.id,
        )
        .first()
    )

    if flag is None:
        return {
            "success": False,
            "message": "Feature flag not found",
        }

    # 3. Check Redis Cache

    cache_key = _build_cache_key(
        environment_name,
        flag_key,
        user_context,
    )

    cached_result = _get_cached_result(cache_key)

    if cached_result is not None:
        cached_result["message"] = "Returned From Redis Cache"
        return cached_result

    # Get user ID

    user_id = user_context.get("user_id")

    if user_id is not None:
        user_id = str(user_id)

    # 4. User Targeting

    if user_id:

        user_rules = (
            db.query(TargetingRule)
            .filter(
                TargetingRule.flag_id == flag.id,
                TargetingRule.rule_type == "user",
                TargetingRule.is_active.is_(True),
            )
            .order_by(TargetingRule.priority)
            .all()
        )

        for rule in user_rules:

            if rule.operator in ("=", "==", "equals"):

                rule_user_id = str(rule.value)

                if user_id == rule_user_id:

                    result = {
                        "success": True,
                        "message": "Matched User Targeting Rule",
                        "environment": environment.name,
                        "flag": flag.key,
                        "enabled": rule.enabled,
                        "value": flag.default_value,
                        "user_context": user_context,
                    }

                    _cache_result(cache_key, result)

                    return result
                
    # 5. Group Targeting

    if user_id:

        group_memberships = (
            db.query(UserGroupMembership)
            .filter(
                UserGroupMembership.user_id == user_id
            )
            .all()
        )

        user_groups = {
            membership.group_name
            for membership in group_memberships
        }

        if user_groups:

            group_rules = (
                db.query(TargetingRule)
                .filter(
                TargetingRule.flag_id == flag.id,
                TargetingRule.rule_type == "group",
                TargetingRule.is_active.is_(True),
                )
                .order_by(TargetingRule.priority)
                .all()
            )

            for rule in group_rules:

                if rule.operator in ("=", "==", "equals"):

                    rule_group = str(rule.value)

                    if rule_group in user_groups:

                        result = {
                            "success": True,
                            "message": "Matched Group Targeting Rule",
                            "environment": environment.name,
                            "flag": flag.key,
                            "enabled": rule.enabled,
                            "value": flag.default_value,
                            "user_context": user_context,
                        }

                        _cache_result(cache_key, result)

                        return result

    # 6. Percentage Rollout

    if user_id:

        percentage_rules = (
            db.query(TargetingRule)
            .filter(
                TargetingRule.flag_id == flag.id,
                TargetingRule.rule_type == "percentage",
                TargetingRule.is_active.is_(True),
            )
            .order_by(TargetingRule.priority)
            .all()
        )

        for rule in percentage_rules:

            percentage = rule.percentage

            if percentage is None:
                continue

            if percentage <= 0:
                continue

            if percentage >= 100:

                result = {
                    "success": True,
                    "message": "Matched Percentage Rollout",
                    "environment": environment.name,
                    "flag": flag.key,
                    "enabled": rule.enabled,
                    "value": flag.default_value,
                    "user_context": user_context,
                }

                _cache_result(cache_key, result)

                return result

            # Deterministic hash
            hash_input = f"{user_id}:{flag.key}"

            hash_value = hashlib.sha256(
                hash_input.encode("utf-8")
            ).hexdigest()

            bucket = int(hash_value, 16) % 100

            if bucket < percentage:

                result = {
                    "success": True,
                    "message": "Matched Percentage Rollout",
                    "environment": environment.name,
                    "flag": flag.key,
                    "enabled": rule.enabled,
                    "value": flag.default_value,
                    "user_context": user_context,
                }

                _cache_result(cache_key, result)

                return result

    # 7. Default Flag Evaluation

    result = {
        "success": True,
        "message": "Default Flag Evaluation",
        "environment": environment.name,
        "flag": flag.key,
        "enabled": flag.enabled,
        "value": flag.default_value,
    }

    _cache_result(cache_key, result)

    return result
