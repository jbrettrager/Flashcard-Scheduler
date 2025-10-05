from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Flashcard
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

