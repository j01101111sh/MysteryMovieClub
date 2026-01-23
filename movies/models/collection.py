import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.urls import reverse

from movies.managers import CollectionQuerySet

from .mystery import MysteryTitle

logger = logging.getLogger(__name__)


class Collection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="collections",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(
        default=True,
        help_text="Can other users see this collection?",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        items: models.QuerySet[CollectionItem]

    objects = CollectionQuerySet.as_manager()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.name} by {self.user}"

    def get_absolute_url(self) -> str:
        return reverse("movies:collection_detail", kwargs={"pk": self.pk})


class CollectionItem(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="items",
    )
    movie = models.ForeignKey(
        MysteryTitle,
        on_delete=models.CASCADE,
        related_name="collection_items",
    )
    order = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True, help_text="Why is this movie in the list?")

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["collection", "movie"],
                name="unique_collection_item",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.movie} in {self.collection}"
