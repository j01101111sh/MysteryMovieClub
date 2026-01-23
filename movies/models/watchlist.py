import logging

from django.conf import settings
from django.db import models

from movies.models import MysteryTitle

logger = logging.getLogger(__name__)


class WatchListEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist",
    )
    movie = models.ForeignKey(
        MysteryTitle,
        on_delete=models.CASCADE,
        related_name="watchlist_entries",
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"],
                name="unique_watchlist_entry",
            ),
        ]
        ordering = ["-added_at"]
        verbose_name_plural = "Watchlist entries"

    def __str__(self) -> str:
        return f"{self.user} wants to watch {self.movie}"
