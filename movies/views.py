import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import ReviewForm, TagVoteForm
from .models import Director, MysteryTitle, Review, Series, Tag, TagVote

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

        return context


class TagVoteView(LoginRequiredMixin, SingleObjectMixin, View):
    """
    Handles upvoting/tagging a movie.
    If the user has already voted for this tag on this movie, the vote is removed (toggled).
    If not, the vote is added.
    """

    model = MysteryTitle

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        form = TagVoteForm(request.POST)

        if form.is_valid():
            tag = form.cleaned_data["tag"]
            self._toggle_vote(request.user, tag)
        elif "tag_id" in request.POST:
            # Handle button clicks from the list of existing tags
            tag_id = request.POST.get("tag_id")
            tag = get_object_or_404(Tag, pk=tag_id)
            self._toggle_vote(request.user, tag)
        else:
            messages.error(request, "Invalid tag selection.")

        return redirect(self.object.get_absolute_url())

    def _toggle_vote(self, user: Any, tag: Tag) -> None:
        vote_query = TagVote.objects.filter(movie=self.object, tag=tag, user=user)
        if vote_query.exists():
            vote_query.delete()
            messages.success(self.request, f"Removed vote for '{tag.name}'.")
        else:
            TagVote.objects.create(movie=self.object, tag=tag, user=user)
            messages.success(self.request, f"Voted for '{tag.name}'.")


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


class DirectorListView(ListView):
    model = Director
    template_name = "movies/director_list.html"
    context_object_name = "directors"


class DirectorDetailView(DetailView):
    model = Director
    template_name = "movies/director_detail.html"
    context_object_name = "director"


class SeriesListView(ListView):
    model = Series
    template_name = "movies/series_list.html"
    context_object_name = "series_list"


class SeriesDetailView(DetailView):
    model = Series
    template_name = "movies/series_detail.html"
    context_object_name = "series"


class ReviewListView(ListView):
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
