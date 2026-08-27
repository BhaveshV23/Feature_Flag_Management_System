from app.cache.redis_client import redis_client
from app.database.config import settings


def test_redis_client_uses_bounded_configuration():
    connection_kwargs = redis_client.connection_pool.connection_kwargs
    retry = connection_kwargs["retry"]

    assert connection_kwargs["host"] == settings.REDIS_HOST
    assert connection_kwargs["port"] == settings.REDIS_PORT
    assert connection_kwargs["socket_connect_timeout"] == settings.REDIS_SOCKET_CONNECT_TIMEOUT
    assert connection_kwargs["socket_timeout"] == settings.REDIS_SOCKET_TIMEOUT
    assert retry._retries == settings.REDIS_RETRIES
    assert connection_kwargs["retry_on_error"] == []

