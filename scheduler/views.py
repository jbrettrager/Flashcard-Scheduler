from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import ReviewResult
from .serializers import ReviewResultSerializer
from .services import process_review


# Create your views here.
class ReviewAPIView(APIView):
    def post(self, request):
        serializer = ReviewResultSerializer(data=request.data)
        if serializer.is_valid():
            review_instance = serializer.save()
            due_date = process_review(
                user_id=review_instance.userID,
                flashcard=review_instance.flashcard,
                rating=review_instance.rating,
                idempotency_key=review_instance.idempotency_key,
            )
            return Response({'new_due_date': due_date})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DueCardsAPIView(APIView):
    def get(self, request, user_id):
        until_timestamp = request.query_params.get('until')

        if not until_timestamp:
            return Response({'error': 'No until date attached to request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            until_time = datetime.fromisoformat(until_timestamp)
        except ValueError:
            return Response({'error': 'Invalid until time. Please use timestamps in ISO8601 format.'}, status=status.HTTP_400_BAD_REQUEST)

        due_cards = ReviewResult.objects.filter(userID=user_id, due_date__lte=until_time)

        result = [{'flashcard_vocab': r.flashcard.vocab, 'due_date': r.due_date} for r in due_cards]

        return Response(result, status=status.HTTP_200_OK)
