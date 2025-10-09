from django.utils import timezone
from zoneinfo import ZoneInfo
from scheduler.models.models import ReviewResult, Flashcard, ReviewRating
import uuid

def get_due_cards(user_id, until_time):
    result = []

    utc_until_time = until_time.astimezone(ZoneInfo('UTC'))

    original_timezone = until_time.tzinfo

    cards = Flashcard.objects.all()

    for card in cards:
        review = ReviewResult.objects.filter(userID=user_id, flashcard=card).order_by('-submit_date').first()

        if not review:
            # Create empty ReviewResult if no result exists
            random_idempotency_key = str(uuid.uuid4()) # Generate random idempotency key
            review = ReviewResult.objects.create(
                userID = user_id,
                flashcard=card,
                rating=ReviewRating.FORGOT,
                submit_date=timezone.now(),
                due_date=timezone.now(),
                idempotency_key=random_idempotency_key
            )
        if review.due_date <= utc_until_time:
            due_date_converted = review.get_converted_due_date(original_timezone)
            result.append({
                'id': card.id,
                'vocab': card.vocab,
                'due_date': due_date_converted,
            })

    return result

