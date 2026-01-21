import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import Q
from django.views.generic import DetailView, ListView

from movies.models import Director, MysteryTitle, Series

logger = logging.getLogger(__name__)


class DirectorListView(ListView):
    model = Director
    template_name = "movies/director_list.html"
    context_object_name = "directors"


class DirectorDetailView(DetailView):
    model = Director
    template_name = "movies/director_detail.html"
    context_object_name = "director"

    if TYPE_CHECKING:
        movies: models.QuerySet[MysteryTitle]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Get all movies for this director
        movies = (
            self.object.movies.all()
            .filter(
                Q(avg_difficulty__gt=0) | Q(avg_quality__gt=0),
            )
            .only("title", "slug", "avg_difficulty", "avg_quality")
        )

        # Prepare data for the scatter plot
        plot_data = [
            {
                "title": movie.title,
                "x": movie.avg_difficulty,
                "y": movie.avg_quality,
                "url": movie.get_absolute_url(),
            }
            for movie in movies
        ]

        # Calculate averages for the lines
        stats = movies.aggregate(
            avg_diff=models.Avg("avg_difficulty"),
            avg_qual=models.Avg("avg_quality"),
        )

        context["plot_data"] = plot_data
        context["avg_difficulty"] = stats["avg_diff"] or 0.0
        context["avg_quality"] = stats["avg_qual"] or 0.0
        return context


class SeriesListView(ListView):
    model = Series
    template_name = "movies/series_list.html"
    context_object_name = "series_list"


class SeriesDetailView(DetailView):
    model = Series
    template_name = "movies/series_detail.html"
    context_object_name = "series"
