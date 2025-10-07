from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dateutil.parser import isoparse, parse
from .services import process_review, get_due_cards


# Create your views here.
class ReviewAPIView(APIView):
    def post(self, request):
        updated_due_jst = process_review(request.data)

        return Response({'new_due_date': updated_due_jst.isoformat()})

class DueCardsAPIView(APIView):
    def get(self, request, user_id):
        until_timestamp = request.query_params.get('until')

        if not until_timestamp:
            return Response({'error': 'No until date attached to request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            until_time = parse(until_timestamp)
        except ValueError:
            return Response({'error': 'Invalid until time. Please use timestamps in ISO8601 format.'}, status=status.HTTP_400_BAD_REQUEST)

        parsed_user_id = int(user_id)
        due_cards = get_due_cards(parsed_user_id, until_time)

        result = [{'flashcard_vocab': card['vocab'], 'due_date': card['due_date']} for card in due_cards]

        return Response(result, status=status.HTTP_200_OK)
