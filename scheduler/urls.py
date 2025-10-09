from django.urls import path
from scheduler.views.views_due_cards import DueCardsAPIView
from scheduler.views.views_review import ReviewAPIView

urlpatterns = [
    path('review/', ReviewAPIView.as_view(), name='review'),
    path('users/<int:user_id>/due-cards/', DueCardsAPIView.as_view(), name='due-cards'),
]