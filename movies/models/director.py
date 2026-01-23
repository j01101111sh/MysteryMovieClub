import logging

from django.db import models
from django.urls import reverse

logger = logging.getLogger(__name__)


class Director(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(
        unique=True,
        help_text="URL friendly name (e.g. rian-johnson)",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("movies:director_detail", kwargs={"slug": self.slug})
