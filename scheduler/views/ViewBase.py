from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from abc import ABC, abstractmethod

class BaseAPIView(APIView, ABC):
    REQUIRED_FIELDS = {}

    def validate_json(self, data):
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in data:
                return False, f"Field {field} is required."
            if not isinstance(data[field], expected_type):
                return False, f"Field {field} is not of type {expected_type}"
        return True, None

    def success(self, data, code=status.HTTP_200_OK):
        return Response(data, status=code)
    def error(self, message, code=status.HTTP_400_BAD_REQUEST):
        return Response({"error": message}, status=code)




class PostAPIView(BaseAPIView):
    def post(self, request, *args, **kwargs):
        is_valid, error = self.validate_json(request.data)
        if not is_valid:
            return self.error(error)
        return self.handle(request, *args, **kwargs)

    @abstractmethod
    def handle(self, request, *args, **kwargs):
        pass

class GetAPIView(BaseAPIView):
    REQUIRED_QUERY_PARAMS = {}

    def get(self, request, *args, **kwargs):
        is_valid, error = self.validate_json(request.data)
        if not is_valid:
            return self.error(error)
        return self.handle(request, *args, **kwargs)

    def handle(self, request, *args, **kwargs):
        pass

    def validate_query_params(self, params):
        for field, expected_type in self.REQUIRED_QUERY_PARAMS.items():
            if field not in params:
                return False, f"Query Parameter {field} is required."

            value = params[field]
            try:
                if expected_type == int:
                    int(value)
                elif expected_type == str:
                    str(value)
                elif expected_type.__name__ == "datetime":
                    from datetime import datetime
                    datetime.fromisoformat(value)
                else:
                    expected_type(value)
            except ValueError:
                return False, f"Invalid value for '{field}', must be {expected_type.__name__}"

        return True, None
