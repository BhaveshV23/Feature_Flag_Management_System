import time

import pytest
import requests

from app.middleware.flag_client import FlagClient


BASE_URL = "http://127.0.0.1:8000"
ENVIRONMENT = "development"


def create_client(
    cache_ttl=30,
    stale_ttl=60,
    use_stale_cache=True,
):
    return FlagClient(
        base_url=BASE_URL,
        environment=ENVIRONMENT,
        cache_ttl=cache_ttl,
        stale_ttl=stale_ttl,
        timeout=2,
        use_stale_cache=use_stale_cache,
    )


def test_cache_miss_calls_api(monkeypatch):

    client = create_client()

    api_calls = []

    def mock_post(url, **kwargs):

        api_calls.append(url)

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    result = client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    assert result["enabled"] is True
    assert len(api_calls) == 1

    stats = client.cache_stats()

    assert stats["misses"] == 1
    assert stats["hits"] == 0


def test_cache_hit_does_not_call_api(monkeypatch):

    client = create_client()

    api_calls = []

    def mock_post(url, **kwargs):

        api_calls.append(url)

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    assert len(api_calls) == 1

    stats = client.cache_stats()

    assert stats["misses"] == 1
    assert stats["hits"] == 1


def test_cache_expires(monkeypatch):

    client = create_client(
        cache_ttl=1
    )

    api_calls = []

    def mock_post(url, **kwargs):

        api_calls.append(url)

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    time.sleep(1.2)

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    assert len(api_calls) == 2

    stats = client.cache_stats()

    assert stats["misses"] == 2


def test_different_users_have_separate_cache_entries(
    monkeypatch,
):

    client = create_client()

    api_calls = []

    def mock_post(url, **kwargs):

        api_calls.append(
            kwargs["json"]
        )

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_002"},
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_002"},
    )

    # Only first request for each user should hit API
    assert len(api_calls) == 2

    stats = client.cache_stats()

    assert stats["misses"] == 2
    assert stats["hits"] == 2
    assert stats["cached_items"] == 2


def test_clear_flag(monkeypatch):

    client = create_client()

    api_calls = []

    def mock_post(url, **kwargs):

        api_calls.append(url)

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    user_context = {
        "user_id": "user_001"
    }

    client.evaluate(
        "dark_mode",
        user_context,
    )

    client.evaluate(
        "dark_mode",
        user_context,
    )

    assert len(api_calls) == 1

    client.clear_flag(
        "dark_mode",
        user_context,
    )

    client.evaluate(
        "dark_mode",
        user_context,
    )

    assert len(api_calls) == 2


def test_clear_cache(monkeypatch):

    client = create_client()

    api_calls = []

    def mock_post(url, **kwargs):

        api_calls.append(url)

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    client.evaluate(
        "dark_mode",
        {"user_id": "user_002"},
    )

    assert client.cache_stats()["cached_items"] == 2

    client.clear_cache()

    assert client.cache_stats()["cached_items"] == 0


def test_is_enabled(monkeypatch):

    client = create_client()

    def mock_post(url, **kwargs):

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    result = client.is_enabled(
        "dark_mode",
        {"user_id": "user_001"},
    )

    assert result is True


def test_get_value(monkeypatch):

    client = create_client()

    def mock_post(url, **kwargs):

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "premium",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        mock_post,
    )

    result = client.get_value(
        "plan_type",
        {"user_id": "user_001"},
    )

    assert result == "premium"


def test_stale_cache_when_api_fails(monkeypatch):

    client = create_client(
        cache_ttl=1,
        stale_ttl=10,
        use_stale_cache=True,
    )

    def successful_post(url, **kwargs):

        class MockResponse:

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "success": True,
                    "enabled": True,
                    "value": "true",
                }

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "post",
        successful_post,
    )

    original_result = client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    time.sleep(1.2)

    def failed_post(url, **kwargs):
        raise requests.ConnectionError(
            "Feature Flag API unavailable"
        )

    monkeypatch.setattr(
        requests,
        "post",
        failed_post,
    )

    stale_result = client.evaluate(
        "dark_mode",
        {"user_id": "user_001"},
    )

    assert stale_result == original_result

    stats = client.cache_stats()

    assert stats["stale_hits"] == 1


def test_api_failure_without_stale_cache_raises(
    monkeypatch,
):

    client = create_client(
        use_stale_cache=False
    )

    def failed_post(url, **kwargs):

        raise requests.ConnectionError(
            "Feature Flag API unavailable"
        )

    monkeypatch.setattr(
        requests,
        "post",
        failed_post,
    )

    with pytest.raises(
        requests.ConnectionError
    ):

        client.evaluate(
            "dark_mode",
            {"user_id": "user_001"},
        )