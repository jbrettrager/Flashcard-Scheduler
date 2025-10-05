from datetime import timedelta
from django.utils import timezone
from .models import ReviewResult, Flashcard

def process_review(user_id, flashcard, rating, idempotency_key):
    # Check idempotency_key
    already_exists = ReviewResult.objects.filter(idempotency_key=idempotency_key).first()
    if already_exists: return already_exists.due_date

    flashcard_instance = Flashcard.objects.get(id=flashcard)

    last_review = ReviewResult.objects.filter(userID=user_id, flashcard=flashcard_instance).order_by('due_date').first()

    next_due = timezone.now()

    if rating == 0:
        next_due = next_due + timedelta(minutes=1)
    elif not last_review:
        if rating == 1:
            next_due = next_due + timedelta(days=5)
        elif rating == 2:
            next_due = next_due + timedelta(days=15)
    else:
        base = timedelta(days=15 if rating == 2 else 5)
        next_due = max(last_review.due_date, next_due + base)

    review, created = ReviewResult.objects.update_or_create(
        userID=user_id,
        flashcard=flashcard_instance,
        defaults={
            'rating':rating,
            'idempotency_key':idempotency_key,
            'due_date':next_due,
        }

    )
    return review.due_date


