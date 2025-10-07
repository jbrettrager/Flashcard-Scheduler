from datetime import timedelta
from django.utils import timezone
from zoneinfo import ZoneInfo
from .models import ReviewResult, Flashcard, ReviewRating

# POST /review services
def process_review(review):
    # Check idempotency_key
    existing_entry = ReviewResult.objects.filter(idempotency_key=review['idempotency_key']).first()
    if existing_entry:
        existing_due_jst = convert_timezone(existing_entry.due_date, "Asia/Tokyo")
        return existing_due_jst

    flashcard_instance = Flashcard.objects.get(id=review['flashcard'])

    last_review = ReviewResult.objects.filter(userID=review['userID'], flashcard=flashcard_instance).order_by('due_date').first()

    next_due = get_next_due_date(review['rating'], last_review)

    next_due_jst = convert_timezone(next_due, 'Asia/Tokyo')

    ReviewResult.objects.update_or_create(
        userID=review['userID'],
        flashcard=flashcard_instance,
        defaults={
            'rating':review['rating'],
            'idempotency_key':review['idempotency_key'],
            'due_date':next_due,
        }

    )
    return next_due_jst

def get_next_due_date(rating, prev_review):
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

def convert_timezone(timestamp, time_zone_name):
    return timestamp.astimezone(ZoneInfo(time_zone_name))

# GET /due-cards service
def get_due_cards(user_id, until_time):
    cards = Flashcard.objects.all()
    result = []
    utc_until_time = convert_timezone(until_time, 'UTC')

    for card in cards:
        review = ReviewResult.objects.filter(userID=user_id, flashcard=card).order_by('-due_date').first()

        if not review:
            review = ReviewResult.objects.create(
                userID = user_id,
                flashcard=card,
                rating=ReviewRating.FORGOT,
                due_date=timezone.now(),
                idempotency_key="none"
            )
        if review.due_date <= utc_until_time:
            due_date_jst = convert_timezone(review.due_date, 'Asia/Tokyo').isoformat()
            result.append({
                'id': card.id,
                'vocab': card.vocab,
                'due_date': due_date_jst,
            })

    return result



