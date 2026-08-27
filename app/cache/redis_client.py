import redis
from redis.backoff import NoBackoff
from redis.retry import Retry

from app.database.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
    socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
    retry=Retry(NoBackoff(), retries=settings.REDIS_RETRIES),
)
