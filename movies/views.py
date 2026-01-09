from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView

from .forms import ReviewForm
from .models import Director, MysteryTitle, Review, Series


class MysteryDetailView(DetailView):
    model = MysteryTitle
    template_name = "movies/mystery_detail.html"
    context_object_name = "movie"

    def get_context_data(self, **kwargs):
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
    template_name = "home.html"
    context_object_name = "movies"


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

    def get_queryset(self):
        self.movie = get_object_or_404(MysteryTitle, slug=self.kwargs["slug"])
        return (
            Review.objects.filter(movie=self.movie)
            .select_related("user")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movie"] = self.movie
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "movies/review_form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.movie = get_object_or_404(MysteryTitle, slug=self.kwargs["slug"])
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            messages.warning(self.request, "You have already reviewed this movie.")
            return redirect(form.instance.movie.get_absolute_url())

    def get_success_url(self):
        return self.object.movie.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movie"] = get_object_or_404(MysteryTitle, slug=self.kwargs["slug"])
        return context
