from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta
from scheduler.models import Flashcard, ReviewResult, ReviewRating

class DueCardsAPITest(APITestCase):
    def setUp(self):
        self.userID = 103
        self.flashcard1 = Flashcard.objects.create(vocab="Testing GET endpoint, card 1")
        self.flashcard2 = Flashcard.objects.create(vocab="Testing GET endpoint, card 2")

        self.due_soon = timezone.now() + timedelta(minutes=1)
        self.due_later = timezone.now() + timedelta(days=15)

        ReviewResult.objects.create(
            flashcard=self.flashcard1,
            userID=self.userID,
            rating=ReviewRating.INSTANT,
            due_date=self.due_later,
            submit_date=timezone.now(),
            idempotency_key='dueAPITestKey1'
        )
        ReviewResult.objects.create(
            flashcard=self.flashcard2,
            userID=self.userID,
            rating=ReviewRating.FORGOT,
            due_date=self.due_soon,
            submit_date=timezone.now(),
            idempotency_key='dueAPITestKey2'
        )

        self.url=reverse('due-cards',kwargs={'user_id':self.userID})

    def test_get_due_cards(self):
        until_time = (timezone.now() + timedelta(days=7)).isoformat()
        response = self.client.get(self.url, {'until': until_time}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        returned_cards = [item['flashcard_vocab'] for item in data]
        self.assertNotIn(self.flashcard1.vocab, returned_cards)
        self.assertIn(self.flashcard2.vocab, returned_cards)

    def test_user_id_validation(self):
        response = self.client.get(self.url, {'userID': "not a number"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_until_time_validation(self):
        response = self.client.get(self.url, {'until': "not an ISO 8601 timestamp"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)