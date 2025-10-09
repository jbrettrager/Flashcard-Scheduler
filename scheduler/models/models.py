from django.db import models
from zoneinfo import ZoneInfo


# Create your models here.

class ReviewRating(models.IntegerChoices):
    FORGOT = 0,
    REMEMBERED = 1,
    INSTANT = 2
class Flashcard(models.Model):
    vocab = models.CharField(max_length=255)

    def __str__(self):
        return self.vocab

class ReviewResult(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    userID = models.IntegerField()
    rating = models.IntegerField(choices=ReviewRating.choices)
    submit_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    idempotency_key = models.CharField(max_length=255, unique=True)

    def get_converted_due_date(self, tzinfo=None):
        tzinfo = tzinfo or ZoneInfo("UTC")
        return self.due_date.astimezone(tzinfo).isoformat()

