from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase

from datetime import timedelta, datetime

from scheduler.models import Flashcard, ReviewResult, ReviewRating
from scheduler.serializers import FlashcardSerializer, ReviewResultSerializer


# Create your tests here.

# Flashcard Model Tests
class FlashcardModelTest(TestCase):
    def test_flashcard_creation(self):
        card = Flashcard.objects.create(vocab="Testing")
        self.assertEqual(card.vocab, "Testing")

class FlashcardSerializerTest(TestCase):
    def test_serializer_validation(self):
        data = {'vocab': 'Testing'}
        serializer = FlashcardSerializer(data=data)
        self.assertTrue(serializer.is_valid())

# ReviewResult Model Tests
class ReviewResultModelTest(TestCase):
    def setUp(self):
        self.userID = 100
        self.flashcard = Flashcard.objects.create(vocab="Testing")
        self.review = ReviewResult.objects.create(
            userID=self.userID,
            flashcard=self.flashcard,
            rating=ReviewRating.INSTANT,
            due_date=timezone.now() + timedelta(days=30),
            idempotency_key='asdfjkl')

    def test_create_review_result(self):

        self.assertEqual(self.review.userID, self.userID)
        self.assertEqual(self.review.flashcard, self.flashcard)
        self.assertEqual(self.review.rating, ReviewRating.INSTANT)
        self.assertEqual(self.review.idempotency_key, 'asdfjkl')

class ReviewResultSerializerTest(TestCase):
    def setUp(self):
        self.userID = 101
        self.flashcard = Flashcard.objects.create(vocab="Serializer Testing")

    def test_serializer_validation(self):
        serializer = ReviewResultSerializer(data={
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.FORGOT,
            'due_date': timezone.now() + timedelta(minutes=1),
            'idempotency_key': 'serializerTest'
        })
        if not serializer.is_valid(): print(serializer.errors)
        self.assertTrue(serializer.is_valid())
        review_instance = serializer.save()

        self.assertEqual(review_instance.userID, self.userID)
        self.assertEqual(review_instance.flashcard, self.flashcard)
        self.assertEqual(review_instance.rating, ReviewRating.FORGOT)
        self.assertEqual(review_instance.idempotency_key, 'serializerTest')

    def test_serializer_output(self):
        review_instance = ReviewResult.objects.create(
            flashcard=self.flashcard,
            userID=self.userID,
            rating=ReviewRating.FORGOT,
            due_date=timezone.now() + timedelta(minutes=1),
            idempotency_key='serializerTest'
        )

        serializer = ReviewResultSerializer(review_instance)
        data = serializer.data

        self.assertEqual(data['flashcard'], self.flashcard.id)
        self.assertEqual(data['userID'], self.userID)
        self.assertEqual(data['rating'], ReviewRating.FORGOT)
        self.assertEqual(data['idempotency_key'], 'serializerTest')

# POST /review API Endpoint Tests
class ReviewAPITest(APITestCase):
    def setUp(self):
        self.userID = 102
        self.flashcard = Flashcard.objects.create(vocab="Testing API")
        self.url = reverse('review')
        self.payload = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.REMEMBERED,
            'idempotency_key': 'reviewAPItest'
        }

    def test_post_review_endpoint(self):
        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('new_due_date', data)

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
            idempotency_key='dueAPITestKey1'
        )
        ReviewResult.objects.create(
            flashcard=self.flashcard2,
            userID=self.userID,
            rating=ReviewRating.FORGOT,
            due_date=self.due_soon,
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

class MonotonicIntervalTest(APITestCase):
    def setUp(self):
        self.userID = 105
        self.flashcard = Flashcard.objects.create(vocab="Testing Monotonic Interval")

        self.url = reverse('review')
        self.review_payload_1 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.INSTANT,
            'idempotency_key': "monotonicAPITest"
        }
        self.review_payload_2 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.REMEMBERED,
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
            'idempotency_key': "checkOnForgot1"
        }
        self.review_payload_2 = {
            'flashcard': self.flashcard.id,
            'userID': self.userID,
            'rating': ReviewRating.FORGOT,
            "idempotency_key": "checkOnForgot2"
        }

    def test_overwrite_on_forgot(self):
        first_response = self.client.post(self.url, self.review_payload_1, format='json')
        first_data = first_response.json()
        first_dt = datetime.fromisoformat(first_data['new_due_date'])

        second_response = self.client.post(self.url, self.review_payload_2, format='json')
        second_data = second_response.json()
        second_dt = datetime.fromisoformat(second_data['new_due_date'])

        self.assertTrue(second_dt < first_dt)


