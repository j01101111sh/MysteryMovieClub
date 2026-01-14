from django.urls import path

from .views import (
    DirectorDetailView,
    DirectorListView,
    MysteryDetailView,
    MysteryListView,
    ReviewCreateView,
    ReviewListView,
    SeriesDetailView,
    SeriesListView,
)

app_name = "movies"

urlpatterns = [
    path("directors/", DirectorListView.as_view(), name="director_list"),
    path(
        "directors/<slug:slug>/",
        DirectorDetailView.as_view(),
        name="director_detail",
    ),
    path("series/", SeriesListView.as_view(), name="series_list"),
    path("series/<slug:slug>/", SeriesDetailView.as_view(), name="series_detail"),
    path("<slug:slug>/review/", ReviewCreateView.as_view(), name="add_review"),
    path("<slug:slug>/reviews/", ReviewListView.as_view(), name="review_list"),
    path("<slug:slug>/", MysteryDetailView.as_view(), name="detail"),
    path("", MysteryListView.as_view(), name="list"),
]
