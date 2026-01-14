import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView

from movies.forms import ReviewForm
from movies.models import MysteryTitle, Review

DEFAULT_PAGE_SIZE = 15

logger = logging.getLogger(__name__)


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
