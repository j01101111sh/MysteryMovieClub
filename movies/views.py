from django.views.generic import DetailView
from .models import MysteryTitle


class MysteryDetailView(DetailView):
    model = MysteryTitle
    template_name = "movies/mystery_detail.html"
    context_object_name = "movie"
