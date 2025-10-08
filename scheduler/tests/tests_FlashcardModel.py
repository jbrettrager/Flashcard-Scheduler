from django.test import TestCase
from scheduler.models import Flashcard
from scheduler.serializers import FlashcardSerializer

class FlashcardModelTest(TestCase):
    def test_flashcard_creation(self):
        card = Flashcard.objects.create(vocab="Testing")
        self.assertEqual(card.vocab, "Testing")

class FlashcardSerializerTest(TestCase):
    def test_serializer_validation(self):
        data = {'vocab': 'Testing'}
        serializer = FlashcardSerializer(data=data)
        self.assertTrue(serializer.is_valid())
