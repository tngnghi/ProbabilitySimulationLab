from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "simstat",
    broker=settings.redis_url,
    backend=settings.redis_url  # use Redis for result storage too
)

# Configure task defaults
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)