import logging
from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from movies.forms import CollectionForm
from movies.models import Collection, CollectionItem, MysteryTitle

logger = logging.getLogger(__name__)


class CollectionListView(ListView):
    model = Collection
    template_name = "movies/collection_list.html"
    context_object_name = "collections"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Collection]:
        queryset = Collection.objects.select_related("user").filter(is_public=True)
        if self.request.user.is_authenticated:
            # Show public collections OR user's own collections
            # We can't easily combine distinct queries in a simple list view without Q objects
            # but for simplicity, let's show all public ones.
            # Users can see their own in a separate profile tab or filter.
            # Let's actually show both: public + own private ones.
            from django.db.models import Q

            queryset = Collection.objects.select_related("user").filter(
                Q(is_public=True) | Q(user=self.request.user),
            )
        return queryset


class CollectionDetailView(DetailView):
    model = Collection
    template_name = "movies/collection_detail.html"
    context_object_name = "collection"

    def get_object(self, queryset: QuerySet[Any] | None = None) -> Collection:
        obj = super().get_object(queryset)
        collection = cast(Collection, obj)

        if not collection.is_public and collection.user != self.request.user:
            from django.http import Http404

            raise Http404("Collection not found")

        return collection

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["items"] = self.object.items.select_related(  # type: ignore
            "movie",
            "movie__director",
        ).order_by("order")
        return context


class CollectionCreateView(LoginRequiredMixin, CreateView):
    model = Collection
    form_class = CollectionForm
    template_name = "movies/collection_form.html"

    def form_valid(self, form: CollectionForm) -> HttpResponse:
        form.instance.user = self.request.user
        messages.success(self.request, "Collection created successfully!")
        return super().form_valid(form)


class CollectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name = "movies/collection_form.html"

    def test_func(self) -> bool:
        return bool(self.get_object().user == self.request.user)


class CollectionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Collection
    template_name = "movies/collection_confirm_delete.html"
    success_url = reverse_lazy("movies:collection_list")

    def test_func(self) -> bool:
        return bool(self.get_object().user == self.request.user)

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        messages.success(request, "Collection deleted.")
        return super().delete(request, *args, **kwargs)


class CollectionAddItemView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int, movie_slug: str) -> HttpResponse:
        collection = get_object_or_404(Collection, pk=pk, user=request.user)
        movie = get_object_or_404(MysteryTitle, slug=movie_slug)

        if CollectionItem.objects.filter(collection=collection, movie=movie).exists():
            messages.warning(request, f"{movie.title} is already in {collection.name}.")
        else:
            CollectionItem.objects.create(collection=collection, movie=movie)
            messages.success(request, f"Added {movie.title} to {collection.name}.")

        return redirect(movie.get_absolute_url())


class CollectionRemoveItemView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self) -> bool:
        item = get_object_or_404(CollectionItem, pk=self.kwargs["pk"])
        return item.collection.user == self.request.user

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        item = get_object_or_404(CollectionItem, pk=pk)
        collection_url = item.collection.get_absolute_url()
        item.delete()
        messages.success(request, "Item removed from collection.")
        return redirect(collection_url)
