from django.views.generic import DetailView, ListView
from .models import MysteryTitle


class MysteryDetailView(DetailView):
    model = MysteryTitle
    template_name = "movies/mystery_detail.html"
    context_object_name = "movie"


class MysteryListView(ListView):
    model = MysteryTitle
    template_name = "home.html"
    context_object_name = "movies"
