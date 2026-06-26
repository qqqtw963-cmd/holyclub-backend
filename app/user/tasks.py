import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def task_korea_timezone():
    logger.info("korea")
    logger.info(timezone.now().minute)
