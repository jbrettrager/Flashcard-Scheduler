from rest_framework import serializers
from scheduler.models.models import Flashcard, ReviewResult
def validate_vocab(value):
    if not value:
        raise serializers.ValidationError('vocab cannot be empty')
    return value

def validate_review(value):
    if not value:
        raise serializers.ValidationError('review cannot be empty')
class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id','vocab']

class ReviewResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewResult
        fields = ['id', 'flashcard', 'userID', 'rating', 'due_date', 'idempotency_key']