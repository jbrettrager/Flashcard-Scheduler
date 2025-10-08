from datetime import timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from scheduler.models.models import ReviewResult, Flashcard, ReviewRating
from datetime import datetime

# POST /review services
def process_review(review):
    # Get user timezone
    timestamp_dt = datetime.fromisoformat(review['timestamp'])
    original_timezone = timestamp_dt.tzinfo

    # Check idempotency
    repeat_entry = ReviewResult.objects.filter(idempotency_key=review['idempotency_key']).first()
    if repeat_entry:
        existing_due = repeat_entry.get_converted_due_date(original_timezone)
        return existing_due

    # Get flashcard from ID
    flashcard_instance = Flashcard.objects.get(id=review['flashcard'])

    # Get most recent review
    last_review = ReviewResult.objects.filter(userID=review['userID'], flashcard=flashcard_instance).order_by('-submit_date').first()


    next_due = get_next_due_date(review['rating'], last_review)
    next_due_converted_tz = next_due.astimezone(original_timezone).isoformat()

    ReviewResult.objects.create(
        userID=review['userID'],
        flashcard=flashcard_instance,
        rating=review['rating'],
        submit_date=review['timestamp'],
        idempotency_key=review['idempotency_key'],
        due_date=next_due)

    return next_due_converted_tz

def get_next_due_date(rating, prev_review):
    # TODO: Change to a more robust algorithm
    next_due = timezone.now()
    if rating == 0:
        next_due = next_due + timedelta(minutes=1)
    elif not prev_review:
        if rating == 1:
            next_due = next_due + timedelta(days=5)
        elif rating == 2:
            next_due = next_due + timedelta(days=15)
    else:
        base = timedelta(days=15 if rating == 2 else 5)
        next_due = max(prev_review.due_date, next_due + base)
    return next_due

# GET /due-cards service
def get_due_cards(user_id, until_time):
    result = []

    utc_until_time = until_time.astimezone(ZoneInfo('UTC'))

    original_timezone = until_time.tzinfo

    cards = Flashcard.objects.all()

    for card in cards:
        review = ReviewResult.objects.filter(userID=user_id, flashcard=card).order_by('-submit_date').first()

        if not review:
            # Create empty ReviewResult if no result exists
            review = ReviewResult.objects.create(
                userID = user_id,
                flashcard=card,
                rating=ReviewRating.FORGOT,
                submit_date=timezone.now(),
                due_date=timezone.now(),
                idempotency_key="none"
            )
        if review.due_date <= utc_until_time:
            due_date_converted = review.get_converted_due_date(original_timezone)
            result.append({
                'id': card.id,
                'vocab': card.vocab,
                'due_date': due_date_converted,
            })

    return result



