from rest_framework import serializers
from .models import Flashcard

def validate_vocab(value):
    if not value:
        raise serializers.ValidationError('vocab cannot be empty')
    return value
class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id','vocab']

