from scheduler.services.services_review import process_review
from scheduler.views.ViewBase import PostAPIView


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
