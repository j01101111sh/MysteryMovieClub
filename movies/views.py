from django.views.generic import DetailView, ListView

from .models import Director, MysteryTitle


class MysteryDetailView(DetailView):
    model = MysteryTitle
    template_name = "movies/mystery_detail.html"
    context_object_name = "movie"


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
