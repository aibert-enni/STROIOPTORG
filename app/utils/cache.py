import logging

from django.core.cache import cache

from redis.exceptions import ConnectionError

logger = logging.getLogger(__name__)

def safe_cache_get(key, default=None):
    try:
        value = cache.get(key)
        if value is None:
            value = default
        return value
    except ConnectionError as e:
        logger.warning(f"Cache GET failed for key={key}: Error with connection to Redis")
        return None
    except Exception as e:
        logger.warning(f"Cache GET failed for key={key}: {str(e)}")
        return None

def safe_cache_set(key, value, timeout=None):
    try:
        cache.set(key, value, timeout)
    except ConnectionError as e:
        logger.warning(f"Cache GET failed for key={key}: Error with connection to Redis")
    except Exception as e:
        logger.warning(f"Cache SET failed for key={key}: {e}")

def safe_cache_delete(key):
    try:
        cache.delete(key)
    except ConnectionError as e:
        logger.warning(f"Cache GET failed for key={key}: Error with connection to Redis")
    except Exception as e:
        logger.warning(f"Cache DELETE failed for key={key}: {e}")