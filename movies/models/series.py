import logging
from typing import TYPE_CHECKING

from django.db import models
from django.urls import reverse

from .mystery import MysteryTitle

logger = logging.getLogger(__name__)


class Series(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(
        unique=True,
        help_text="URL friendly name (e.g. benoit-blanc)",
    )

    if TYPE_CHECKING:
        movies: models.QuerySet[MysteryTitle]

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "series"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("movies:series_detail", kwargs={"slug": self.slug})
