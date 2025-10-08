from django.contrib import admin
from scheduler.models.models import Flashcard, ReviewResult

# Register your models here.
admin.site.register(Flashcard)
admin.site.register(ReviewResult)