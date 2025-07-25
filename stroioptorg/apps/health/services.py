import logging

from django.db import connection

from apps.health.utils import get_redis, get_elasticsearch

logger = logging.getLogger(__name__)

class ServiceHealthChecker:

    @staticmethod
    def check_database_detailed():
        """Detailed database health check"""
        try:
            # Connection check
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            # Performance check
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                migration_count = cursor.fetchone()[0]

            # Connection pool info
            queries_count = len(connection.queries)

            response = {
                'status': 'healthy',
                'migration_count': migration_count,
                'queries_executed': queries_count,
                'vendor': connection.vendor,
            }

            if connection.vendor == 'postgresql':
                response['version'] = connection.get_server_version()

            return response

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)

    }

    @staticmethod
    def check_redis_detailed():
        try:
            r = get_redis()

            r.ping()

            info = r.info()

            return {
                'status': 'healthy',
                'version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses')
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

    @staticmethod
    def check_elasticsearch_detailed():
        try:
            es = get_elasticsearch()

            if not es.ping():
                raise Exception(f"Elasticsearch connection failed")

            health = es.cluster.health()

            nodes = es.nodes.info()

            return {
                'status': 'healthy',
                'cluster_name': health.get('cluster_name'),
                'cluster_status': health.get('status'),
                'number_of_nodes': health.get('number_of_nodes'),
                'active_primary_shards': health.get('active_primary_shards'),
                'active_shards': health.get('active_shards'),
                'relocating_shards': health.get('relocating_shards'),
                'initializing_shards': health.get('initializing_shards'),
                'unassigned_shards': health.get('unassigned_shards')
            }
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }