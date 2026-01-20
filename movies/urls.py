from django.urls import path

from .views import (
    CollectionAddItemView,
    CollectionCreateView,
    CollectionDeleteView,
    CollectionDetailView,
    CollectionItemUpdateView,
    CollectionListView,
    CollectionRemoveItemView,
    CollectionUpdateView,
    DirectorDetailView,
    DirectorListView,
    MysteryDetailView,
    MysteryListView,
    ReviewCreateView,
    ReviewListView,
    SeriesDetailView,
    SeriesListView,
    TagVoteView,
    WatchListToggleView,
    WatchListView,
)

app_name = "movies"

urlpatterns = [
    # Collections
    path("collections/", CollectionListView.as_view(), name="collection_list"),
    path(
        "collections/create/",
        CollectionCreateView.as_view(),
        name="collection_create",
    ),
    path(
        "collections/<int:pk>/",
        CollectionDetailView.as_view(),
        name="collection_detail",
    ),
    path(
        "collections/<int:pk>/update/",
        CollectionUpdateView.as_view(),
        name="collection_update",
    ),
    path(
        "collections/<int:pk>/delete/",
        CollectionDeleteView.as_view(),
        name="collection_delete",
    ),
    path(
        "collections/<int:pk>/add/<slug:movie_slug>/",
        CollectionAddItemView.as_view(),
        name="collection_add_item",
    ),
    path(
        "collections/item/<int:pk>/remove/",
        CollectionRemoveItemView.as_view(),
        name="collection_remove_item",
    ),
    path(
        "collections/item/<int:pk>/edit/",
        CollectionItemUpdateView.as_view(),
        name="collection_item_edit",
    ),
    # Directors
    path("directors/", DirectorListView.as_view(), name="director_list"),
    path(
        "directors/<slug:slug>/",
        DirectorDetailView.as_view(),
        name="director_detail",
    ),
    # Series
    path("series/", SeriesListView.as_view(), name="series_list"),
    path("series/<slug:slug>/", SeriesDetailView.as_view(), name="series_detail"),
    # Watchlist
    path("watchlist/", WatchListView.as_view(), name="watchlist"),
    path(
        "<slug:slug>/watchlist/toggle/",
        WatchListToggleView.as_view(),
        name="watchlist_toggle",
    ),
    # Reviews
    path("<slug:slug>/review/", ReviewCreateView.as_view(), name="add_review"),
    path("<slug:slug>/reviews/", ReviewListView.as_view(), name="review_list"),
    # Tags
    path("<slug:slug>/vote-tag/", TagVoteView.as_view(), name="vote_tag"),
    # Movies
    path("<slug:slug>/", MysteryDetailView.as_view(), name="detail"),
    path("", MysteryListView.as_view(), name="list"),
]
