import hashlib
import json
import threading
import time

import requests


class FlagClient:
    """
    Client-side feature flag helper.

    Provides local in-memory caching for evaluated feature flags
    and reduces repeated requests to the Feature Flag API.
    """

    def __init__(
        self,
        base_url: str,
        environment: str,
        cache_ttl: int = 30,
        stale_ttl: int = 60,
        timeout: int = 5,
        use_stale_cache: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.environment = environment

        self.cache_ttl = cache_ttl
        self.stale_ttl = stale_ttl
        self.timeout = timeout
        self.use_stale_cache = use_stale_cache

        self._cache = {}
        self._lock = threading.Lock()

        self._hits = 0
        self._misses = 0
        self._stale_hits = 0

    def _build_cache_key(
        self,
        flag_key: str,
        user_context: dict | None = None,
    ) -> str:

        context = user_context or {}

        context_json = json.dumps(
            context,
            sort_keys=True,
            separators=(",", ":"),
        )

        context_hash = hashlib.sha256(
            context_json.encode("utf-8")
        ).hexdigest()

        return (
            f"{self.environment}:"
            f"{flag_key}:"
            f"{context_hash}"
        )

    def _get_cached_value(self, cache_key: str):

        with self._lock:

            cached = self._cache.get(cache_key)

            if cached is None:
                return None

            value, expires_at, stale_until = cached

            now = time.time()

            # Fresh cache
            if now < expires_at:

                self._hits += 1

                return {
                    "value": value,
                    "is_stale": False,
                }

            # Stale cache
            if now < stale_until:

                return {
                    "value": value,
                    "is_stale": True,
                }

            # Completely expired
            del self._cache[cache_key]

            return None

    def _set_cached_value(
        self,
        cache_key: str,
        value,
    ):

        now = time.time()

        expires_at = now + self.cache_ttl

        stale_until = (
            expires_at + self.stale_ttl
        )

        with self._lock:

            self._cache[cache_key] = (
                value,
                expires_at,
                stale_until,
            )

    def evaluate(
        self,
        flag_key: str,
        user_context: dict | None = None,
    ):
        """
        Evaluate a feature flag.

        Fresh local cache:
            Return immediately.

        Cache miss/stale cache:
            Call the Feature Flag API.

        API failure with stale cache:
            Return stale value if enabled.
        """

        cache_key = self._build_cache_key(
            flag_key,
            user_context,
        )

        cached = self._get_cached_value(
            cache_key
        )

        stale_value = None

        if cached is not None:

            if not cached["is_stale"]:

                return cached["value"]

            stale_value = cached["value"]

        # Count this as an API/cache miss
        self._misses += 1

        try:

            response = requests.post(
                f"{self.base_url}/evaluate",
                json={
                    "flag_key": flag_key,
                    "environment_name": self.environment,
                    "user_context": user_context,
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            result = response.json()

            self._set_cached_value(
                cache_key,
                result,
            )

            return result

        except requests.RequestException:

            if (
                self.use_stale_cache
                and stale_value is not None
            ):

                self._stale_hits += 1

                return stale_value

            raise

    def is_enabled(
        self,
        flag_key: str,
        user_context: dict | None = None,
    ) -> bool:

        result = self.evaluate(
            flag_key=flag_key,
            user_context=user_context,
        )

        return bool(
            result.get("enabled", False)
        )

    def get_value(
        self,
        flag_key: str,
        user_context: dict | None = None,
    ):

        result = self.evaluate(
            flag_key=flag_key,
            user_context=user_context,
        )

        return result.get("value")

    def clear_cache(self):

        with self._lock:
            self._cache.clear()

    def clear_flag(
        self,
        flag_key: str,
        user_context: dict | None = None,
    ):

        cache_key = self._build_cache_key(
            flag_key,
            user_context,
        )

        with self._lock:

            self._cache.pop(
                cache_key,
                None,
            )

    def cache_stats(self):

        total = (
            self._hits
            + self._misses
        )

        hit_rate = (
            (self._hits / total) * 100
            if total > 0
            else 0
        )

        return {
            "hits": self._hits,
            "misses": self._misses,
            "stale_hits": self._stale_hits,
            "total_requests": total,
            "hit_rate": round(
                hit_rate,
                2,
            ),
            "cached_items": len(
                self._cache
            ),
        }