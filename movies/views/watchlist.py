import logging
from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from movies.models import MysteryTitle, WatchListEntry
from users.models import CustomUser

logger = logging.getLogger(__name__)


class WatchListView(LoginRequiredMixin, ListView):
    model = WatchListEntry
    template_name = "movies/watchlist.html"
    context_object_name = "watchlist_entries"
    paginate_by = 15

    def get_queryset(self) -> QuerySet[WatchListEntry]:
        # cast is needed because mypy thinks request.user might be AnonymousUser despite LoginRequiredMixin
        user = cast(CustomUser, self.request.user)
        return WatchListEntry.objects.filter(
            user=user,
        ).select_related("movie", "movie__director")


class WatchListToggleView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        movie = get_object_or_404(MysteryTitle, slug=slug)

        # cast is needed here as well for the get_or_create call
        user = cast(CustomUser, request.user)

        entry, created = WatchListEntry.objects.get_or_create(
            user=user,
            movie=movie,
        )

        if not created:
            entry.delete()
            logger.info("User %s removed %s from watchlist", user, movie)
        else:
            logger.info("User %s added %s to watchlist", user, movie)

        # Redirect back to the movie detail page
        return redirect(movie.get_absolute_url())
