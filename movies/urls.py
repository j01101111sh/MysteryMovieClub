from django.urls import path

from .views import MysteryDetailView

app_name = "movies"

urlpatterns = [
    path("<slug:slug>/", MysteryDetailView.as_view(), name="detail"),
]
