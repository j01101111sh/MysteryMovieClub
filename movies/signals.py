# movies/signals.py
import logging
from typing import Any

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

# Added WatchListEntry to imports
from movies.models import (
    Director,
    MysteryTitle,
    Review,
    Series,
    Tag,
    TagVote,
    WatchListEntry,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_movie_stats(sender: type[Review], instance: Review, **kwargs: Any) -> None:
    """
    Update aggregate statistics and invalidate heatmap cache.
    """
    # 1. Update DB Aggregates
    instance.movie.update_stats()

    # 2. Invalidate Heatmap Cache
    # Key must match the arguments used in the template: 'heatmap' and [movie.pk]
    key = make_template_fragment_key("heatmap", [instance.movie.pk])
    cache.delete(key)

    logger.info("Invalidated heatmap cache for movie: %s", instance.movie.slug)


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


@receiver(post_save, sender=WatchListEntry)
def log_watchlist_entry_creation(
    sender: type[WatchListEntry],
    instance: WatchListEntry,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new watchlist entry is created."""
    if created:
        logger.info(
            "Watchlist entry created: %s added %s to watchlist",
            instance.user,
            instance.movie.slug,
        )


@receiver(post_delete, sender=WatchListEntry)
def log_watchlist_entry_deletion(
    sender: type[WatchListEntry],
    instance: WatchListEntry,
    **kwargs: Any,
) -> None:
    """Log a message whenever a watchlist entry is deleted."""
    logger.info(
        "Watchlist entry removed: %s removed %s from watchlist",
        instance.user,
        instance.movie.slug,
    )
