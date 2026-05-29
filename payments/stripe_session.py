import stripe
from django.conf import settings
from payments.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing):
    days = (borrowing.expected_return_date - borrowing.borrow_date).days
    total_price = int(borrowing.book.daily_fee * 100)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": borrowing.book.title},
                    "unit_amount": total_price,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/success/",
        cancel_url="http://localhost:8000/cancel/",
    )
    Payment.objects.create(
        status=Payment.StausChoices.PENDING,
        type=Payment.TypeChoices.PAYMENT,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=days + borrowing.book.daily_fee,
    )
