from celery import shared_task

from borrowings import overdue_borrowings


@shared_task
def check_overdue_borrowings():
    overdue_borrowings.message_telegram()
