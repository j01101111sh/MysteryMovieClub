import logging
from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView

from movies.forms import ReviewForm
from movies.models import MysteryTitle, Review, ReviewHelpfulVote
from movies.views.mixins import ElidedPaginationMixin
from users.models import CustomUser

logger = logging.getLogger(__name__)


class ReviewListView(ElidedPaginationMixin, ListView):
    model = Review
    template_name = "movies/review_list.html"
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Review]:
        self.movie = get_object_or_404(MysteryTitle, slug=self.kwargs["slug"])
        return (
            Review.objects.filter(movie=self.movie)
            .select_related("user")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["movie"] = self.movie

        # Add user's helpful votes for vote button highlighting
        if self.request.user.is_authenticated:
            # Get the list of reviews on the current page
            page_reviews = context.get("reviews", [])

            # Fetch votes only for these specific reviews
            votes = ReviewHelpfulVote.objects.filter(
                user=self.request.user,
                review__in=page_reviews,
            ).select_related("review")

            # Map review.pk to vote object for efficient lookup
            vote_map = {vote.review_id: vote for vote in votes}

            # Attach the vote object directly to the review instance
            for review in page_reviews:
                review.user_vote = vote_map.get(review.pk)

        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "movies/review_form.html"

    def form_valid(self, form: ReviewForm) -> HttpResponse:
        form.instance.user = self.request.user
        form.instance.movie = get_object_or_404(MysteryTitle, slug=self.kwargs["slug"])
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            messages.warning(self.request, "You have already reviewed this movie.")
            return redirect(form.instance.movie.get_absolute_url())

    def get_success_url(self) -> str:
        if self.object is not None:
            return str(self.object.movie.get_absolute_url())
        raise AttributeError

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["movie"] = get_object_or_404(MysteryTitle, slug=self.kwargs["slug"])
        return context


class ReviewHelpfulVoteView(LoginRequiredMixin, View):
    """
    Handle voting on whether a review was helpful or not.

    POST parameters:
    - is_helpful: "true" for helpful, "false" for not helpful

    If the user has already voted the same way, the vote is removed.
    If the user voted differently, the vote is updated.
    """

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """
        Process a helpful vote on a review.

        Args:
            request: The HTTP request
            pk: The primary key of the review

        Returns:
            Redirect to the review's movie page or JSON response for AJAX
        """
        review = get_object_or_404(Review, pk=pk)
        user = cast(CustomUser, request.user)

        # Prevent users from voting on their own reviews
        if review.user == user:
            messages.warning(request, "You cannot vote on your own review.")
            return self._get_response(request, review)

        # Get the vote type from POST data
        is_helpful_str = request.POST.get("is_helpful")
        if is_helpful_str not in ("true", "false"):
            return HttpResponseBadRequest("Missing or invalid 'is_helpful' parameter.")
        is_helpful = is_helpful_str == "true"

        # Check if user has already voted
        existing_vote = ReviewHelpfulVote.objects.filter(
            review=review,
            user=user,
        ).first()

        if existing_vote:
            if existing_vote.is_helpful == is_helpful:
                # Same vote - remove it (toggle off)
                existing_vote.delete()
                vote_type = "helpful" if is_helpful else "not helpful"
                messages.success(
                    request,
                    f"Removed your '{vote_type}' vote.",
                )
            else:
                # Different vote - update it
                existing_vote.is_helpful = is_helpful
                existing_vote.save()
                vote_type = "helpful" if is_helpful else "not helpful"
                messages.success(
                    request,
                    f"Changed your vote to '{vote_type}'.",
                )
        else:
            # New vote
            ReviewHelpfulVote.objects.create(
                review=review,
                user=user,
                is_helpful=is_helpful,
            )
            vote_type = "helpful" if is_helpful else "not helpful"
            messages.success(
                request,
                f"Marked review as '{vote_type}'.",
            )

        return self._get_response(request, review)

    def _get_response(self, request: HttpRequest, review: Review) -> HttpResponse:
        """
        Return appropriate response based on request type.

        Args:
            request: The HTTP request
            review: The review that was voted on

        Returns:
            JSON response for AJAX requests, redirect for normal requests
        """
        # Check if this is an AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Refresh review stats
            review.refresh_from_db()

            # Get user's current vote
            user_vote = None
            if request.user.is_authenticated:
                vote = ReviewHelpfulVote.objects.filter(
                    review=review,
                    user=request.user,
                ).first()
                if vote:
                    user_vote = vote.is_helpful

            return JsonResponse(
                {
                    "success": True,
                    "helpful_count": review.helpful_count,
                    "not_helpful_count": review.not_helpful_count,
                    "helpfulness_score": review.helpfulness_score,
                    "user_vote": user_vote,
                },
            )

        next_url = request.GET.get("next")
        if next_url and request.user.is_authenticated:
            return redirect(next_url)

        return redirect_to_login(request.get_full_path(), login_url=reverse("login"))
