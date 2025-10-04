from django.test import TestCase
from scheduler.models import Flashcard

# Create your tests here.
class FlashcardModelTest(TestCase):
    def test_flashcard_creation(self):
        card = Flashcard.objects.create(vocab="Testing")
        self.assertEqual(card.vocab, "Testing")