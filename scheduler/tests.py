from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from scheduler.models import Flashcard, ReviewResult, ReviewRating
from scheduler.serializers import FlashcardSerializer


# Create your tests here.
# Flashcard Model Tests
class FlashcardModelTest(TestCase):
    def test_flashcard_creation(self):
        card = Flashcard.objects.create(vocab="Testing")
        self.assertEqual(card.vocab, "Testing")

    def test_serializer_validation(self):
        data = {'vocab': 'Testing'}
        serializer = FlashcardSerializer(data=data)
        self.assertTrue(serializer.is_valid())

# ReviewResult Model Tests
class ReviewResultModelTest(TestCase):
    def setUp(self):
        self.userID = 100
        self.flashcard = Flashcard.objects.create(vocab="Testing")

    def test_create_review_result(self):
        review = ReviewResult.objects.create(
            userID=self.userID,
            flashcard=self.flashcard,
            rating=ReviewRating.INSTANT,
            due_date=timezone.now() + timedelta(days=30),
            idempotency_key='asdfjkl')
        self.assertEqual(review.userID, self.userID)
        self.assertEqual(review.flashcard, self.flashcard)
        self.assertEqual(review.rating, ReviewRating.INSTANT)
        self.assertEqual(review.idempotency_key, 'asdfjkl')