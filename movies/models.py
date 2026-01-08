from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Director(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(
        unique=True, help_text="URL friendly name (e.g. rian-johnson)"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("movies:director_detail", kwargs={"slug": self.slug})


class Series(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(
        unique=True, help_text="URL friendly name (e.g. benoit-blanc)"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "series"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("movies:series_detail", kwargs={"slug": self.slug})


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
    directors = models.ManyToManyField(
        "Director", related_name="movies", help_text="Director or Creator"
    )
    series = models.ForeignKey(
        "Series",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="movies",
    )
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


class Review(models.Model):
    movie = models.ForeignKey(
        MysteryTitle, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Rating (1-5)"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "user"], name="unique_review_per_user"
            )
        ]

    def __str__(self):
        return f"{self.user}'s review of {self.movie}"
