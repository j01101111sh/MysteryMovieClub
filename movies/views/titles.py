import logging
from typing import Any

from django.db.models import Count, Q, QuerySet
from django.views.generic import DetailView, ListView

from movies.forms import TagVoteForm
from movies.models import MysteryTitle, Tag, WatchListEntry

DEFAULT_PAGE_SIZE = 15

logger = logging.getLogger(__name__)


class MysteryDetailView(DetailView):
    model = MysteryTitle
    template_name = "movies/mystery_detail.html"
    context_object_name = "movie"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Review data
        reviews = self.object.reviews.select_related("user").order_by("-created_at")
        context["recent_reviews"] = reviews[:3]
        context["total_reviews_count"] = reviews.count()
        if self.request.user.is_authenticated:
            context["has_reviewed"] = self.object.reviews.filter(
                user=self.request.user,
            ).exists()

        # Tag data
        # Aggregate votes for each tag on this movie
        tags_with_counts = (
            Tag.objects.filter(votes__movie=self.object)
            .annotate(vote_count=Count("votes"))
            .order_by("-vote_count", "name")
        )
        context["tags_with_counts"] = tags_with_counts

        # Pass the form for adding new tags
        context["tag_form"] = TagVoteForm()

        # Get the set of Tag IDs the current user has voted for
        if self.request.user.is_authenticated:
            context["user_voted_tag_ids"] = set(
                self.object.tag_votes.filter(user=self.request.user).values_list(
                    "tag_id",
                    flat=True,
                ),
            )
        else:
            context["user_voted_tag_ids"] = set()

        # Watchlist status
        if self.request.user.is_authenticated:
            context["in_watchlist"] = WatchListEntry.objects.filter(
                user=self.request.user,
                movie=self.object,
            ).exists()
        else:
            context["in_watchlist"] = False

        return context


class MysteryListView(ListView):
    model = MysteryTitle
    template_name = "movies/movie_list.html"
    context_object_name = "movies"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet[MysteryTitle]:
        # Start with the default queryset (ordered by release year)
        queryset = super().get_queryset()

        # Get the search query from the URL parameters
        self.query = self.request.GET.get("q")

        if self.query:
            # Log the search action
            logger.info("Search query received: %s", self.query)

            # Filter by title, description, or director name
            queryset = queryset.filter(
                Q(title__icontains=self.query)
                | Q(description__icontains=self.query)
                | Q(director__name__icontains=self.query),
            )

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if context.get("is_paginated"):
            context["elided_page_range"] = context["paginator"].get_elided_page_range(
                context["page_obj"].number,
                on_each_side=2,
                on_ends=1,
            )
        context["search_query"] = self.query
        return context
