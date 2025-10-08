from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from dateutil.parser import isoparse
from scheduler.models import Flashcard, ReviewRating

class ReviewAPITest(APITestCase):
    def setUp(self):
        self.userID = 102
        self.flashcard = Flashcard.objects.create(vocab="Testing API")
        self.url = reverse('review')
        self.payload = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.REMEMBERED,
            'timestamp': timezone.now(),
            'idempotency_key': 'reviewAPItest'
        }
        self.bad_payload = {
            'notTheRightKey': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.REMEMBERED,
            'timestamp': timezone.now(),
            'idempotency_key': 'reviewAPItest'
        }

    def test_post_review_endpoint(self):
        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('new_due_date', data)

    def test_review_json_validation(self):
        response = self.client.post(self.url, self.bad_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MonotonicIntervalTest(APITestCase):
    def setUp(self):
        self.userID = 105
        self.flashcard = Flashcard.objects.create(vocab="Testing Monotonic Interval")

        self.url = reverse('review')
        self.review_payload_1 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.INSTANT,
            'timestamp': timezone.now(),
            'idempotency_key': "monotonicAPITest"
        }
        self.review_payload_2 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.REMEMBERED,
            'timestamp': timezone.now(),
            "idempotency_key": "monotonicAPITest2"
        }

    def test_monotonic_interval(self):
        first_response = self.client.post(self.url, self.review_payload_1, format='json')
        first_data = first_response.json()
        first_due_date = first_data['new_due_date']

        second_response = self.client.post(self.url, self.review_payload_2, format='json')
        second_data = second_response.json()
        second_due_date = second_data['new_due_date']

        self.assertEqual(first_due_date, second_due_date)

class OverwriteDueDateOnForgotTest(APITestCase):
    def setUp(self):
        self.userID = 106
        self.flashcard = Flashcard.objects.create(vocab="Testing On Forgot")

        self.url = reverse('review')
        self.review_payload_1 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.INSTANT,
            'timestamp': timezone.now(),
            'idempotency_key': "checkOnForgot1"
        }
        self.review_payload_2 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.FORGOT,
            'timestamp': timezone.now(),
            "idempotency_key": "checkOnForgot2"
        }

    def test_overwrite_on_forgot(self):
        first_response = self.client.post(self.url, self.review_payload_1, format='json')
        first_data = first_response.json()
        first_dt = isoparse(first_data['new_due_date'])

        second_response = self.client.post(self.url, self.review_payload_2, format='json')
        second_data = second_response.json()
        second_dt = isoparse(second_data['new_due_date'])

        self.assertTrue(second_dt < first_dt)
