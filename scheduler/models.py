from django.db import models

# Create your models here.
class Flashcard(models.Model):
    vocab = models.CharField(max_length=255)

    def __str__(self):
        return self.vocab