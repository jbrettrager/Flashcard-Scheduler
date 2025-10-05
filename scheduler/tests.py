from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APITestCase

from datetime import timedelta

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
