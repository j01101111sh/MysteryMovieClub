import logging

from django.conf import settings
from django.db import models

from .mystery import MysteryTitle

logger = logging.getLogger(__name__)


class Review(models.Model):
    movie = models.ForeignKey(
        MysteryTitle,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quality = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name="Quality (1-5)",
    )
    difficulty = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name="Difficulty (1-5)",
    )
    is_fair_play = models.BooleanField(
        verbose_name="Fair Play?",
        help_text="Was the mystery solvable with the clues provided?",
    )
    solved = models.BooleanField(
        default=False,
        verbose_name="Solved?",
        help_text="Did you solve the mystery before the reveal?",
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Helpful Votes",
    )
    not_helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Not Helpful Votes",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["movie", "user"],
                name="unique_review_per_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user}'s review of {self.movie}"

    def update_helpful_stats(self) -> None:
        """Update the helpful vote counts for this review."""
        stats = self.helpful_votes.aggregate(
            helpful=models.Count("id", filter=models.Q(is_helpful=True)),
            not_helpful=models.Count("id", filter=models.Q(is_helpful=False)),
        )
        self.helpful_count = stats["helpful"] or 0
        self.not_helpful_count = stats["not_helpful"] or 0
        self.save(update_fields=["helpful_count", "not_helpful_count"])

    @property
    def helpfulness_score(self) -> float:
        """Calculate a helpfulness percentage (0-100)."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return (self.helpful_count / total) * 100


class ReviewHelpfulVote(models.Model):
    """
    Tracks whether a user found a review helpful or not.
    Each user can vote once per review.
    """

    review = models.ForeignKey(
        "Review",
        on_delete=models.CASCADE,
        related_name="helpful_votes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    is_helpful = models.BooleanField(
        help_text="True if the user found this review helpful, False otherwise",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["review", "user"],
                name="unique_helpful_vote_per_user",
            ),
        ]
        ordering = ["-created_at"]
        verbose_name = "Review Helpful Vote"
        verbose_name_plural = "Review Helpful Votes"

    def __str__(self) -> str:
        vote_type = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user} voted {vote_type} on review #{self.review_id}"
