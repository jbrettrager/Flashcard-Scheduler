from datetime import timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone
from scheduler.models.models import ReviewResult, Flashcard, ReviewRating
from datetime import datetime
from django.db import transaction


@transaction.atomic
def process_review(review):
    # Get user timezone
    timestamp_dt = datetime.fromisoformat(review['timestamp'])
    original_timezone = timestamp_dt.tzinfo

    # Convert timestamp into UTC
    timestamp_utc = timestamp_dt.astimezone(ZoneInfo("UTC"))

    # Check idempotency
    repeat_entry = ReviewResult.objects.filter(idempotency_key=review['idempotency_key']).first()
    if repeat_entry:
        existing_due = repeat_entry.get_converted_due_date(original_timezone)
        return existing_due

    # Get flashcard from ID
    flashcard_instance = Flashcard.objects.get(id=review['flashcard'])

    # Get most recent review
    last_review = ReviewResult.objects.filter(userID=review['userID'], flashcard=flashcard_instance).order_by('-submit_date').first()


    next_due = get_new_due_date(review['rating'], last_review)
    next_due_converted_tz = next_due.astimezone(original_timezone).isoformat()

    ReviewResult.objects.create(
        userID=review['userID'],
        flashcard=flashcard_instance,
        rating=review['rating'],
        submit_date=timestamp_utc,
        idempotency_key=review['idempotency_key'],
        due_date=next_due)

    return next_due_converted_tz

def get_new_due_date(rating, prev_review):
    is_first_review = prev_review is None
    is_incorrect = rating == 0

    now = timezone.now()

    if is_incorrect:
        return now + timedelta(minutes=1)
    elif is_first_review:
        if rating == int(ReviewRating.REMEMBERED):
            return now + timedelta(days=5)
        elif rating == int(ReviewRating.INSTANT):
            return now + timedelta(days=15)

    prev_interval = prev_review.due_date - prev_review.submit_date
    prev_interval_seconds = max(prev_interval.total_seconds(), 60)

    multiplier = 1

    if rating == int(ReviewRating.REMEMBERED):
        multiplier = 1.5
    elif rating == int(ReviewRating.INSTANT):
        multiplier = 2.5

    new_interval = timedelta(seconds=prev_interval_seconds * multiplier)

    new_due_date = now + new_interval

    return new_due_date