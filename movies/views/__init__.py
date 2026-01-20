from .collections import (
    CollectionAddItemView,
    CollectionCreateView,
    CollectionDeleteView,
    CollectionDetailView,
    CollectionItemUpdateView,
    CollectionListView,
    CollectionRemoveItemView,
    CollectionUpdateView,
)
from .reviews import ReviewCreateView, ReviewListView
from .tags import TagVoteView
from .taxonomy import (
    DirectorDetailView,
    DirectorListView,
    SeriesDetailView,
    SeriesListView,
)
from .titles import MysteryDetailView, MysteryListView
from .watchlist import WatchListToggleView, WatchListView

__all__ = [
    "CollectionAddItemView",
    "CollectionCreateView",
    "CollectionDeleteView",
    "CollectionDetailView",
    "CollectionItemUpdateView",
    "CollectionListView",
    "CollectionRemoveItemView",
    "CollectionUpdateView",
    "DirectorDetailView",
    "DirectorListView",
    "MysteryDetailView",
    "MysteryListView",
    "ReviewCreateView",
    "ReviewListView",
    "SeriesDetailView",
    "SeriesListView",
    "TagVoteView",
    "WatchListToggleView",
    "WatchListView",
]
