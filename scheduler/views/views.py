from datetime import datetime
from scheduler.services.services import process_review, get_due_cards
from scheduler.views.ViewBase import PostAPIView, GetAPIView


# /api/review/
class ReviewAPIView(PostAPIView):
    REQUIRED_FIELDS = {
        "userID": int,
        "flashcard": int,
        "rating": int,
        "timestamp": str,
        "idempotency_key": str,
    }
    def handle(self, request, *args, **kwargs):
        updated_due = process_review(request.data)
        return self.success({'new_due_date': updated_due})

# /api/users/{userID}/due-cards/?until={ISO 8601 Timestamp}
class DueCardsAPIView(GetAPIView):
    REQUIRED_QUERY_PARAMS = {
        'until':datetime
    }

    def get(self, request, *args, **kwargs):
        is_valid, error = self.validate_query_params(request.query_params)
        if not is_valid:
            return self.error(error)

        return self.handle(request, *args, **kwargs)
    def handle(self, request, user_id):
        until_timestamp = request.query_params.get('until')
        until_time = datetime.fromisoformat(until_timestamp)

        try:
            parsed_user_id = int(user_id)
        except ValueError:
            return self.error("Invalid userID")
        due_cards = get_due_cards(parsed_user_id, until_time)

        result = [{'flashcard_vocab': card['vocab'], 'flashcard_id': card.id, 'due_date': card['due_date']} for card in due_cards]

        return self.success(result)


