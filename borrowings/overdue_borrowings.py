from django.utils import timezone

from borrowings.models import Borrowing

from notifications import bot_message


def get_overdue_borrowings():
    borrowings = Borrowing.objects.filter(
        expected_return_date__lte=timezone.now(), actual_return_date=None
    )
    return borrowings


def message_telegram():
    overdue_borrowings = get_overdue_borrowings()
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            bot_message.send_message(
                (
                    f"📚 The book has not been returned:\n"
                    f"👤 User: {borrowing.user.email}\n"
                    f"🪪 First Name: {borrowing.user.first_name}\n"
                    f"🪪 Last Name: {borrowing.user.last_name}\n"
                    f"📖 Book: {borrowing.book.title}\n"
                    f"📆 Borrow date: {borrowing.borrow_date}\n"
                    f"📆 Expected return date: {borrowing.expected_return_date}"
                )
            )
    else:
        bot_message.send_message("No borrowings overdue today!")
