from django.urls import path
from .views import ReviewAPIView, DueCardsAPIView

urlpatterns = [
    path('review/', ReviewAPIView.as_view(), name='review'),
    path('users/<int:user_id>/due-cards/', DueCardsAPIView.as_view(), name='due-cards'),
]