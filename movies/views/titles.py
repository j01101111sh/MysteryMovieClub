import logging
from typing import Any

from django.db.models import Count, QuerySet
from django.views.generic import DetailView, ListView

from movies.forms import TagVoteForm
from movies.models import (
    Collection,
    MysteryTitle,
    ReviewHelpfulVote,
    Tag,
    WatchListEntry,
)
from movies.views.mixins import ElidedPaginationMixin  # Import the new mixin

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

        # Convert to list to allow attaching attributes
        recent_reviews = list(reviews[:3])
        context["recent_reviews"] = recent_reviews
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

        # Add user's helpful votes for vote button highlighting
        if self.request.user.is_authenticated:
            # Fetch votes for the specific reviews being displayed
            votes = ReviewHelpfulVote.objects.filter(
                user=self.request.user,
                review__in=recent_reviews,
            ).select_related("review")

            # Map review.pk to vote object
            vote_map = {vote.review_id: vote for vote in votes}

            # Attach vote to review objects
            for review in recent_reviews:
                review.user_vote = vote_map.get(review.pk)

        # Watchlist status
        if self.request.user.is_authenticated:
            context["in_watchlist"] = WatchListEntry.objects.filter(
                user=self.request.user,
                movie=self.object,
            ).exists()
        else:
            context["in_watchlist"] = False

        # User's Collections
        if self.request.user.is_authenticated:
            context["user_collections"] = Collection.objects.filter(
                user=self.request.user,
            ).order_by("-updated_at")
        else:
            context["user_collections"] = []

        return context


class MysteryListView(ElidedPaginationMixin, ListView):
    model = MysteryTitle
    template_name = "movies/movie_list.html"
    context_object_name = "movies"
    paginate_by = DEFAULT_PAGE_SIZE

    query: str | None = None

    def get_queryset(self) -> QuerySet[MysteryTitle]:
        self.query = self.request.GET.get("q")

        # Get all objects -> search if applicable -> order
        return MysteryTitle.objects.search(self.query).order_by("-release_year")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.query
        return context
