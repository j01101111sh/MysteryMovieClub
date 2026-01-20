import logging
import secrets

from django.contrib.auth import get_user_model

# Local imports
from movies.models import MysteryTitle, Tag, TagVote

logger = logging.getLogger(__name__)


def create_tag_votes() -> None:
    """
    Seeds the database with tag votes.
    Requires Users, Movies, and Tags to be seeded first.
    """
    User = get_user_model()
    gen = secrets.SystemRandom()

    logger.info("Seeding tag votes...")

    # 1. Fetch Dependencies
    all_tags = list(Tag.objects.all())
    if not all_tags:
        logger.error("No tags found. Please run seed_tags.py first.")
        return

    movies = list(MysteryTitle.objects.all())
    if not movies:
        logger.error("No movies found. Please run seed_movies.py first.")
        return

    users = list(User.objects.filter(is_superuser=False))
    if not users:
        logger.warning(
            "No standard users found. Creating votes might be limited. Run seed_users.py to generate users.",
        )
        users = list(User.objects.all())

    if not users:
        logger.error("No users found at all. Please run seed_users.py first.")
        return

    logger.info(
        "Found %s tags, %s movies, and %s users.",
        len(all_tags),
        len(movies),
        len(users),
    )

    # 2. Create Tag Votes
    tag_votes_created = 0

    for movie in movies:
        for user in users:
            # Randomly assign 1 to 4 tags per user per movie to simulate activity
            # Use sample to pick unique tags from the list
            num_tags = secrets.randbelow(4) + 1  # 1 to 4 tags
            chosen_tags = gen.sample(all_tags, num_tags)

            for tag in chosen_tags:
                _, created = TagVote.objects.get_or_create(
                    movie=movie,
                    user=user,
                    tag=tag,
                )
                if created:
                    tag_votes_created += 1

    logger.info("Done! Created %s tag votes.", tag_votes_created)
