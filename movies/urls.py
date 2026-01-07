from django.urls import path

from .views import MysteryDetailView, MysteryListView

app_name = "movies"

urlpatterns = [
    path("<slug:slug>/", MysteryDetailView.as_view(), name="detail"),
    path("", MysteryListView.as_view(), name="home"),
]
