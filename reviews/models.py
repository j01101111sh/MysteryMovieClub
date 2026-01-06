from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class MysteryContent(models.Model):
    class ContentType(models.TextChoices):
        MOVIE = "MV", "Movie"
        TV_SHOW = "TV", "TV Show"

    title = models.CharField(max_length=255)
    content_type = models.CharField(
        max_length=2,
        choices=ContentType.choices,
        default=ContentType.MOVIE,
    )
    release_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mystery Title"
        verbose_name_plural = "Mystery Titles"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class Review(models.Model):
    content = models.ForeignKey(
        MysteryContent, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mystery_reviews",
    )

    # Rating 1: Overall Quality (1-5)
    overall_quality = models.PositiveSmallIntegerField(
        help_text="Rate the overall quality from 1 (Poor) to 5 (Masterpiece).",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    # Rating 2: Mystery Difficulty (1-5)
    difficulty = models.PositiveSmallIntegerField(
        help_text="How hard was it to solve? 1 (Obvious) to 5 (Impossible).",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    # Rating 3: Fair Play Assessment
    is_fair_play = models.BooleanField(
        default=True,
        verbose_name="Fair Play Mystery",
        help_text="Check this box if the viewer is given all the clues needed to solve the mystery alongside the detective.",
    )

    comment = models.TextField(blank=True, help_text="Optional review comments.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["content", "user"], name="unique_user_content_review"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} review of {self.content}"
