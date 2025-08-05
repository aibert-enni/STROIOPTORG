import redis
from django.conf import settings
from elasticsearch import Elasticsearch
from redis import Redis


def get_redis() -> Redis:
    redis_conf = {
        'host': settings.REDIS_HOST,
        'port': settings.REDIS_PORT,
        'db': settings.REDIS_DB,
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'decode_responses': True,
    }

    if settings.REDIS_PASSWORD:
        redis_conf['password'] = settings.REDIS_PASSWORD

    r = redis.Redis(**redis_conf)

    return r

def get_elasticsearch() -> Elasticsearch:
    es_config = {
        "hosts": [settings.ES_URL],
        "timeout": 10,
        "max_retries": 3,
        "retry_on_timeout": True,
    }
    if settings.ES_USERNAME and settings.ES_PASSWORD:
        es_config["basic_auth"] = (settings.ES_USERNAME, settings.ES_PASSWORD)

    es = Elasticsearch(**es_config)

    return es