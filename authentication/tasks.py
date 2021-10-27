from celery.utils.log import get_task_logger
from celery.decorators import task

from .utils import EmailHelper


@task(name="send_email_task")
def send_email_task(data):
    return EmailHelper.send_mail(data)