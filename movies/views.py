from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView

from .forms import ReviewForm
from .models import Director, MysteryTitle, Review, Series

DEFAULT_PAGE_SIZE = 15


class MysteryDetailView(DetailView):
    model = MysteryTitle
    template_name = "movies/mystery_detail.html"
    context_object_name = "movie"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        reviews = self.object.reviews.select_related("user").order_by("-created_at")
        context["recent_reviews"] = reviews[:3]
        context["total_reviews_count"] = reviews.count()
        if self.request.user.is_authenticated:
            context["has_reviewed"] = self.object.reviews.filter(
                user=self.request.user
            ).exists()
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
            # Filter by title, description, or director name
            # We use Q objects to perform OR lookups
            queryset = queryset.filter(
                Q(title__icontains=self.query)
                | Q(description__icontains=self.query)
                | Q(director__name__icontains=self.query)
            )

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if context.get("is_paginated"):
            context["elided_page_range"] = context["paginator"].get_elided_page_range(
                context["page_obj"].number, on_each_side=2, on_ends=1
            )
        # Pass the search query back to the template to keep it in the search bar
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
