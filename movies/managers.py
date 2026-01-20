import logging
from typing import TYPE_CHECKING, Self

from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import Q

# Use TYPE_CHECKING to avoid circular imports if users app imports movies
if TYPE_CHECKING:
    from users.models import CustomUser

logger = logging.getLogger(__name__)


class MysteryTitleQuerySet(models.QuerySet):
    def search(self, query: str | None) -> Self:
        """
        Filters titles by title, description, or director name.
        """
        if not query:
            return self

        logger.info("Search query received: %s", query)
        return self.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(director__name__icontains=query),
        )

    def movies(self) -> Self:
        return self.filter(media_type="MV")

    def tv_shows(self) -> Self:
        return self.filter(media_type="TV")

    def fair_play(self) -> Self:
        return self.filter(is_fair_play_candidate=True)


class CollectionQuerySet(models.QuerySet):
    def visible_to(self, user: CustomUser | AnonymousUser) -> Self:
        """
        Returns collections visible to the general public.
        If a user is provided, ensures we don't show them their own
        collections in the 'public' feed.
        """
        qs = self.filter(is_public=True)

        # Check is_authenticated to guard against AnonymousUser
        if user.is_authenticated:
            return qs.exclude(user=user)

        return qs
