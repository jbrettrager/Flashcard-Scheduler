from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from scheduler.models import Flashcard, ReviewResult, ReviewRating
from scheduler.serializers import ReviewResultSerializer
class ReviewResultModelTest(TestCase):
    def setUp(self):
        self.userID = 100
        self.flashcard = Flashcard.objects.create(vocab="Testing")
        self.review = ReviewResult.objects.create(
            userID=self.userID,
            flashcard=self.flashcard,
            submit_date=timezone.now(),
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
