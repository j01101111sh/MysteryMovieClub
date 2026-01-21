import logging
from typing import Any

from django.views.generic import DetailView, ListView

from movies.models import Director, Series

logger = logging.getLogger(__name__)


class DirectorListView(ListView):
    model = Director
    template_name = "movies/director_list.html"
    context_object_name = "directors"


class DirectorDetailView(DetailView):
    model = Director
    template_name = "movies/director_detail.html"
    context_object_name = "director"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Get all movies for this director
        movies = self.object.movies.all()  # type: ignore[attr-defined]

        # Prepare data for the scatter plot
        # We only include movies that have non-zero stats to avoid clustering at (0,0)
        # and ensure the chart is meaningful.
        plot_data = [
            {
                "title": movie.title,
                "x": movie.avg_difficulty,
                "y": movie.avg_quality,
                "url": movie.get_absolute_url(),
            }
            for movie in movies
            if movie.avg_difficulty > 0 or movie.avg_quality > 0
        ]

        # Pass the raw list to the context. Serialization handles by the template.
        context["plot_data"] = plot_data
        return context


class SeriesListView(ListView):
    model = Series
    template_name = "movies/series_list.html"
    context_object_name = "series_list"


class SeriesDetailView(DetailView):
    model = Series
    template_name = "movies/series_detail.html"
    context_object_name = "series"
