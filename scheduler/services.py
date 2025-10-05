from datetime import timedelta
from django.utils import timezone
from .models import ReviewResult

def process_review(user_id, flashcard, rating, idempotency_key):
    # Check idempotency_key
    already_exists = ReviewResult.objects.filter(idempotency_key=idempotency_key).first()
    if already_exists: return already_exists.due_date

    last_review = ReviewResult.objects.filter(userID=user_id, flashcard=flashcard).order_by('due_date').first()

    now = timezone.now()

    if rating == 0:
        next_due = now + timedelta(minutes=1)
    elif not last_review:
        if rating == 1:
            next_due = now + timedelta(days=5)
        elif rating == 2:
            next_due = now + timedelta(days=15)
    else:
        base = timedelta(days=15 if rating == 2 else 5)
        next_due = max(last_review.due_date, now + base)

    review = ReviewResult.objects.create(
        userID=user_id,
        flashcard=flashcard,
        rating=rating,
        idempotency_key=idempotency_key,
        due_date=next_due,
    )
    return review.due_date


