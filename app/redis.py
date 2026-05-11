from arq.connections import RedisSettings
from app.config import settings
from urllib.parse import urlparse

def get_redis_settings() -> RedisSettings:
    """Parse REDIS_URL from settings into arq RedisSettings."""
    url = urlparse(settings.REDIS_URL)
    return RedisSettings(
        host=url.hostname or "localhost",
        port=url.port or 6379,
        database=int(url.path.lstrip('/') or 0),
        password=url.password,
    )
