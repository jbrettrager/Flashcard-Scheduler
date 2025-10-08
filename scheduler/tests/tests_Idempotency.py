from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase
from datetime import timedelta
from scheduler.models import Flashcard,ReviewRating

class IdempotencyTest(APITestCase):
    def setUp(self):
        self.userID = 107
        self.flashcard = Flashcard.objects.create(vocab="Testing Idempotency")
        self.review_url = reverse('review')
        self.due_cards_url = reverse('due-cards', kwargs={'user_id':self.userID})
        self.until_time = timezone.now() + timedelta(days=14)

        self.review_payload_1 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.INSTANT,
            'idempotency_key': "checkIdempotency"
        }

    def test_review_idempotency(self):
        first_response = self.client.post(self.review_url, self.review_payload_1, format='json')
        second_response = self.client.post(self.review_url, self.review_payload_1, format='json')
        self.assertEqual(first_response.json(), second_response.json())

    def test_due_cards_idempotency(self):
        first_response = self.client.get(self.due_cards_url, {'until': self.until_time.isoformat()}, format='json')
        second_response = self.client.get(self.due_cards_url, {'until': self.until_time.isoformat()}, format='json')
        self.assertEqual(first_response.json(), second_response.json())