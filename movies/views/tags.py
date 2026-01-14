import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from movies.forms import TagVoteForm
from movies.models import MysteryTitle, Tag, TagVote

logger = logging.getLogger(__name__)


class TagVoteView(LoginRequiredMixin, SingleObjectMixin, View):
    """
    Handles upvoting/tagging a movie.
    If the user has already voted for this tag on this movie, the vote is removed (toggled).
    If not, the vote is added.
    """

    model = MysteryTitle

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        form = TagVoteForm(request.POST)

        if form.is_valid():
            tag = form.cleaned_data["tag"]
            self._toggle_vote(request.user, tag)
        elif "tag_id" in request.POST:
            # Handle button clicks from the list of existing tags
            tag_id = request.POST.get("tag_id")
            tag = get_object_or_404(Tag, pk=tag_id)
            self._toggle_vote(request.user, tag)
        else:
            messages.error(request, "Invalid tag selection.")

        return redirect(self.object.get_absolute_url())

    def _toggle_vote(self, user: Any, tag: Tag) -> None:
        vote_query = TagVote.objects.filter(movie=self.object, tag=tag, user=user)
        if vote_query.exists():
            vote_query.delete()
            messages.success(self.request, f"Removed vote for '{tag.name}'.")
        else:
            TagVote.objects.create(movie=self.object, tag=tag, user=user)
            messages.success(self.request, f"Voted for '{tag.name}'.")
