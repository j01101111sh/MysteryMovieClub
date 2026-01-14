import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


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


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_movie_stats(sender: type[Review], instance: Review, **kwargs: Any) -> None:
    instance.movie.update_stats()


@receiver(post_save, sender=MysteryTitle)
def log_movie_creation(
    sender: type[MysteryTitle],
    instance: MysteryTitle,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new movie is created."""
    if created:
        logger.info("Movie created: %s", instance.slug)


@receiver(post_save, sender=Review)
def log_review_creation(
    sender: type[Review],
    instance: Review,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new review is created."""
    if created:
        # Uses the Review's __str__ method: "{user}'s review of {movie}"
        logger.info("Review created: %s for %s", instance.user, instance.movie.slug)


@receiver(post_save, sender=Director)
def log_director_creation(
    sender: type[Director],
    instance: Director,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new director is created."""
    if created:
        logger.info("Director created: %s", instance.slug)


@receiver(post_save, sender=Series)
def log_series_creation(
    sender: type[Series],
    instance: Series,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new series is created."""
    if created:
        logger.info("Series created: %s", instance.slug)


@receiver(post_save, sender=Tag)
def log_tag_creation(
    sender: type[Tag],
    instance: Tag,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new tag is created."""
    if created:
        logger.info("Tag created: %s", instance.slug)


@receiver(post_save, sender=TagVote)
def log_tag_vote_creation(
    sender: type[TagVote],
    instance: TagVote,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new tag vote is created."""
    if created:
        logger.info(
            "Tag vote created: %s voted for %s on %s",
            instance.user,
            instance.tag.slug,
            instance.movie.slug,
        )


@receiver(post_delete, sender=TagVote)
def log_tag_vote_deletion(
    sender: type[TagVote],
    instance: TagVote,
    **kwargs: Any,
) -> None:
    """Log a message whenever a tag vote is deleted."""
    logger.info(
        "Tag vote removed: %s voted for %s on %s",
        instance.user,
        instance.tag.slug,
        instance.movie.slug,
    )
