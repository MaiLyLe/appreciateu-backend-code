from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command


logger = get_task_logger(__name__)


@shared_task
def sample_task():
    logger.info("The sample task just ran.")

@shared_task
def delete_courses():
    call_command("del_courses_on_semester_start_and_inform",)

@shared_task
def delete_students_upon_drop_out():
    call_command("del_studs_on_exit_and_inform",)
