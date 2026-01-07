from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class MysteryTitle(models.Model):
    class MediaType(models.TextChoices):
        MOVIE = "MV", _("Movie")
        TV_SHOW = "TV", _("TV Show")
        MINISERIES = "MS", _("Miniseries")

    # Core Metadata
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, help_text="URL friendly title (e.g. knives-out)"
    )
    media_type = models.CharField(
        max_length=2,
        choices=MediaType.choices,
        default=MediaType.MOVIE,
    )
    release_year = models.PositiveIntegerField()
    director = models.CharField(max_length=255, help_text="Director or Creator")
    description = models.TextField(blank=True)

    # Mystery Specifics
    is_fair_play_candidate = models.BooleanField(
        default=True, help_text="Is this title applicable for Fair Play analysis?"
    )

    # Aggregates (Denormalized fields for caching/performance)
    avg_quality = models.FloatField(default=0.0, verbose_name="Quality Score")
    avg_difficulty = models.FloatField(default=0.0, verbose_name="Difficulty Score")
    fair_play_consensus = models.FloatField(
        default=0.0,
        verbose_name="Fair Play %",
        help_text="Percentage of users who voted 'Fair'",
    )

    class Meta:
        ordering = ["-release_year", "title"]
        verbose_name = "Mystery Title"
        verbose_name_plural = "Mystery Titles"

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_absolute_url(self):
        return reverse("movies:detail", kwargs={"slug": self.slug})
