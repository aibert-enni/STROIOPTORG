import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stroioptorg.settings')

app = Celery('stroioptorg')

# read settings from django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# automatically search tasks from apps/tasks
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


