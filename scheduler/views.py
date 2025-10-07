from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .services import process_review, get_due_cards


# Create your views here.
class ReviewAPIView(APIView):
    REQUIRED_FIELDS = {
        "userID": int,
        "flashcard": int,
        "rating": int,
        "idempotency_key": str,
    }
    def post(self, request):

        is_valid, error_msg =  self.validate_request_json(request.data)
        if not is_valid:
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

        updated_due_jst = process_review(request.data)

        return Response({'new_due_date': updated_due_jst})

    def validate_request_json(self, data):
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in data:
                return False, f"Missing required field: {field}"

            if not isinstance(data[field], expected_type):
                return False, f"Field {field} must be of type {expected_type.name__}"
        return True, None

class DueCardsAPIView(APIView):
    def get(self, request, user_id):
        is_valid, error_msg = self.validate_request(request, user_id)
        if not is_valid:
            return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

        until_timestamp = request.query_params.get('until')

        if not until_timestamp:
            return Response({'error': 'No until date attached to request.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            until_time = datetime.fromisoformat(until_timestamp)
        except ValueError:
            return Response({'error': 'Invalid until time. Please use timestamps in ISO8601 format.'}, status=status.HTTP_400_BAD_REQUEST)

        parsed_user_id = int(user_id)
        due_cards = get_due_cards(parsed_user_id, until_time)

        result = [{'flashcard_vocab': card['vocab'], 'due_date': card['due_date']} for card in due_cards]

        return Response(result, status=status.HTTP_200_OK)

    def validate_request(self, request, user_id):
        until_timestamp = request.query_params.get('until')
        if not until_timestamp:
            return False, f"No until date attached to request."
        try:
            until_time = datetime.fromisoformat(until_timestamp)
        except ValueError:
            return False, f"Invalid until time. Please use timestamps in ISO8601 format."

        try:
            int(user_id)
        except ValueError:
            return False, f"Invalid userID. Please use an integer."

        return True, None

