from django.urls import path

from .views import (
    DirectorDetailView,
    DirectorListView,
    MysteryDetailView,
    MysteryListView,
)

app_name = "movies"

urlpatterns = [
    path("directors/", DirectorListView.as_view(), name="director_list"),
    path(
        "directors/<slug:slug>/", DirectorDetailView.as_view(), name="director_detail"
    ),
    path("<slug:slug>/", MysteryDetailView.as_view(), name="detail"),
    path("", MysteryListView.as_view(), name="list"),
]
