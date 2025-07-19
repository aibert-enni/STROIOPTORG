import logging

import redis
from django.conf import settings
from django.core.checks import register, Error, Warning
from django.db import connection
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


@register()
def check_database(app_configs, **kwargs):
    errors = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            if result[0] != 1:
                raise Exception("Database query returned unexpected result")

            from apps.users.models import User
            User.objects.exists()
    except Exception as e:
        errors.append(Error(
            "Database query returned unexpected result",
            hint=f"Error: {str(e)}",
            id="health.E001"
        ))

    return errors


@register()
def check_redis(app_configs, **kwargs):
    errors = []
    try:
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

        r.ping()

        test_key = 'health_check_test'

        test_value = 'health_test'

        r.set(test_key, test_value, ex=10)

        value = r.get(test_key)

        if value != test_value:
            raise Exception("Redis set/get operation failed")

        r.delete(test_key)
    except redis.ConnectionError as e:
        errors.append(Error(
            "Redis connection error",
            hint=f"Cannot connect to Redis server - {settings.REDIS_URL}",
            id="health.E002"
        ))
    except redis.TimeoutError as e:
        errors.append(Error(
            "Redis timeout error",
            hint=f"Redis operation timeout - {str(e)}",
            id="health.E003"
        ))
    except Exception as e:
        errors.append(Warning(
            'Redis operation failed',
            hint=f'Redis basic operations failed - {str(e)}',
            id='health.W001',
        ))

    return errors


@register()
def check_elasticsearch(app_configs, **kwargs):
    from django.core.checks import Error, Warning

    errors = []

    try:
        es_config = {
            "hosts": [settings.ES_URL],
            "timeout": 10,
            "max_retries": 3,
            "retry_on_timeout": True,
        }
        if settings.ES_USERNAME and settings.ES_PASSWORD:
            es_config["basic_auth"] = (settings.ES_USERNAME, settings.ES_PASSWORD)

        es = Elasticsearch(**es_config)

        # Быстрая проверка доступности
        if not es.ping():
            raise Exception("Elasticsearch ping failed")

        health = es.cluster.health()
        cluster_status = health.get("status", "unknown")

        if cluster_status == "red":
            errors.append(Error(
                "Elasticsearch cluster is in RED state",
                hint="Cluster health is critical, some primary shards are not allocated",
                id="health.E004",
            ))
        elif cluster_status == "yellow":
            errors.append(Warning(
                "Elasticsearch cluster is in YELLOW state",
                hint="Cluster health is degraded, some replica shards are not allocated",
                id="health.W002",
            ))

        # --- Round-trip test записи/чтения ---
        test_index = "health_check_test"
        test_id = "health_test"
        test_doc = {
            "message": "health check",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # Запись; refresh='wait_for' гарантирует, что документ попадёт в поисковый сегмент до возврата
        es.index(index=test_index, id=test_id, document=test_doc, refresh="wait_for")

        # Проверка чтения (можно быстрее через get вместо search)
        doc = es.get(index=test_index, id=test_id, ignore=[404])
        if not doc or not doc.get("found"):
            raise Exception("Elasticsearch indexing/get test failed")

        # Очистка: удаляем документ по ID (избегаем delete_by_query + конфликтов версий)
        es.delete(index=test_index, id=test_id, ignore=[404], refresh=True)

    except ImportError:
        errors.append(Warning(
            "Elasticsearch client not available",
            hint="Install elasticsearch package: pip install elasticsearch",
            id="health.W003",
        ))
    except Exception as e:
        errors.append(Error(
            "Elasticsearch connection or operation failed",
            hint=f"Error: {e}",
            id="health.E005",
        ))

    return errors
