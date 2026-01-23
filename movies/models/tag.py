import logging

from django.conf import settings
from django.db import models

from .mystery import MysteryTitle

logger = logging.getLogger(__name__)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TagVote(models.Model):
    movie = models.ForeignKey(
        MysteryTitle,
        on_delete=models.CASCADE,
        related_name="tag_votes",
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "tag", "user"],
                name="unique_tag_vote",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} voted for {self.tag} on {self.movie}"
