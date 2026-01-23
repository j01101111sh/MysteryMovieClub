import logging
from typing import TYPE_CHECKING

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from movies.managers import MysteryTitleQuerySet

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .collection import CollectionItem
    from .review import Review
    from .tag import TagVote
    from .watchlist import WatchListEntry


class MysteryTitle(models.Model):
    class MediaType(models.TextChoices):
        MOVIE = "MV", _("Movie")
        TV_SHOW = "TV", _("TV Show")
        MINISERIES = "MS", _("Miniseries")

    # Core Metadata
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True,
        help_text="URL friendly title (e.g. knives-out)",
    )
    media_type = models.CharField(
        max_length=2,
        choices=MediaType.choices,
        default=MediaType.MOVIE,
    )
    release_year = models.PositiveIntegerField()
    director = models.ForeignKey(
        "Director",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies",
        help_text="Director or Creator",
    )
    series = models.ForeignKey(
        "Series",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies",
    )
    description = models.TextField(blank=True)

    if TYPE_CHECKING:
        reviews: models.QuerySet[Review]
        tag_votes: models.QuerySet[TagVote]
        watchlist_entries: models.QuerySet[WatchListEntry]
        collection_items: models.QuerySet[CollectionItem]

    is_fair_play_candidate = models.BooleanField(
        default=True,
        help_text="Is this title applicable for Fair Play analysis?",
    )

    # Aggregates (Denormalized fields for caching/performance)
    avg_quality = models.FloatField(default=0.0, verbose_name="Quality Score")
    avg_difficulty = models.FloatField(default=0.0, verbose_name="Difficulty Score")
    fair_play_consensus = models.FloatField(
        default=0.0,
        verbose_name="Fair Play %",
        help_text="Percentage of users who voted 'Fair'",
    )

    objects = MysteryTitleQuerySet.as_manager()

    class Meta:
        ordering = ["-release_year", "title"]
        verbose_name = "Mystery Title"
        verbose_name_plural = "Mystery Titles"

    def __str__(self) -> str:
        return f"{self.title} ({self.release_year})"

    def get_absolute_url(self) -> str:
        return reverse("movies:detail", kwargs={"slug": self.slug})

    def get_review_url(self) -> str:
        return reverse("movies:add_review", kwargs={"slug": self.slug})

    def update_stats(self) -> None:
        """Recalculate and save aggregate stats based on reviews."""
        reviews = self.reviews.all()  # noqa
        stats = reviews.aggregate(
            avg_quality=models.Avg("quality"),
            avg_difficulty=models.Avg("difficulty"),
            fair_play_consensus=models.Avg(
                models.Case(
                    models.When(is_fair_play=True, then=100.0),
                    default=0.0,
                    output_field=models.FloatField(),
                ),
            ),
        )
        self.avg_quality = stats["avg_quality"] or 0.0
        self.avg_difficulty = stats["avg_difficulty"] or 0.0
        self.fair_play_consensus = stats["fair_play_consensus"] or 0.0

        self.save(
            update_fields=["avg_quality", "avg_difficulty", "fair_play_consensus"],
        )
