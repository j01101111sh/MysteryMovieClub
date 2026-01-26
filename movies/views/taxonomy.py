import logging
from typing import TYPE_CHECKING, Any, cast

from django.db import models
from django.db.models import Q
from django.views.generic import DetailView, ListView

from movies.models import Director, Series

logger = logging.getLogger(__name__)


class TaxonomyChartMixin:
    """Mixin to provide consistent context data for taxonomy detail views."""

    # Explicitly declare that instances of this mixin will have an 'object' attribute
    # of type Director or Series.
    object: Director | Series

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore[misc]

        # We assume self.object has a 'movies' related manager
        movies_qs = self.object.movies.all()

        # 1. Prepare Plot Data (Quality vs Difficulty)
        # Filter for movies that have at least one metric rated
        rated_movies = movies_qs.filter(
            Q(avg_difficulty__gt=0) | Q(avg_quality__gt=0),
        ).only("title", "slug", "avg_difficulty", "avg_quality", "release_year")

        plot_data = [
            {
                "title": movie.title,
                "x": movie.avg_difficulty,
                "y": movie.avg_quality,
                "url": movie.get_absolute_url(),
            }
            for movie in rated_movies
        ]

        # 2. Calculate Averages
        # We calculate the average of rated items (excluding 0s)
        stats = movies_qs.aggregate(
            avg_qual=models.Avg("avg_quality", filter=Q(avg_quality__gt=0)),
            avg_diff=models.Avg("avg_difficulty", filter=Q(avg_difficulty__gt=0)),
        )

        context["plot_data"] = plot_data
        context["avg_difficulty"] = stats["avg_diff"] or 0.0
        context["avg_quality"] = stats["avg_qual"] or 0.0

        # Explicitly cast context to dict[str, Any] to satisfy mypy strict return check
        return cast(dict[str, Any], context)


class DirectorListView(ListView):
    model = Director
    template_name = "movies/director_list.html"
    context_object_name = "directors"


class DirectorDetailView(TaxonomyChartMixin, DetailView):
    model = Director
    template_name = "movies/director_detail.html"
    context_object_name = "director"

    if TYPE_CHECKING:
        object: Director


class SeriesListView(ListView):
    model = Series
    template_name = "movies/series_list.html"
    context_object_name = "series_list"


class SeriesDetailView(TaxonomyChartMixin, DetailView):
    model = Series
    template_name = "movies/series_detail.html"
    context_object_name = "series"

    if TYPE_CHECKING:
        object: Series
