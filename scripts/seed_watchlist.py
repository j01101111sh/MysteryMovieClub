import logging
import secrets

from django.contrib.auth import get_user_model

from movies.models import MysteryTitle, WatchListEntry

logger = logging.getLogger(__name__)


def create_watchlist_entries() -> None:
    """
    Seeds the database with watchlist entries.
    Requires Users and Movies to be seeded first.
    """
    User = get_user_model()

    logger.info("Seeding watchlist entries...")

    # 1. Fetch Dependencies
    movies = list(MysteryTitle.objects.all())
    if not movies:
        logger.error("No movies found. Please run seed_movies.py first.")
        return

    users = list(User.objects.filter(is_superuser=False))
    if not users:
        logger.warning(
            "No standard users found. Run seed_users.py to generate users.",
        )
        users = list(User.objects.all())

    if not users:
        logger.error("No users found. Please run seed_users.py first.")
        return

    # 2. Create Watchlist Entries
    watchlist_entries_created = 0

    for user in users:
        for movie in movies:
            # Randomly decide to add to watchlist (30% chance)
            if secrets.randbelow(10) < 3:
                _, created = WatchListEntry.objects.get_or_create(
                    user=user,
                    movie=movie,
                )
                if created:
                    watchlist_entries_created += 1

    logger.info("Done! Created %s watchlist entries.", watchlist_entries_created)
