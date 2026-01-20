import logging
import secrets

from django.contrib.auth import get_user_model

from movies.models import MysteryTitle, Review

logger = logging.getLogger(__name__)


def create_reviews() -> None:
    """
    Seeds the database with reviews.
    Requires Users and Movies to be seeded first.
    """
    User = get_user_model()

    logger.info("Seeding reviews...")

    # 1. Fetch Users
    users = list(User.objects.filter(is_superuser=False))
    if not users:
        logger.warning(
            "No standard users found. Creating reviews might be limited. Please run seed_users.py first.",
        )
        users = list(User.objects.all())

    if not users:
        logger.error("No users found at all. Please run seed_users.py first.")
        return

    logger.info("Found %s users to create reviews for.", len(users))

    # 2. Fetch Movies
    movies = list(MysteryTitle.objects.all())
    if not movies:
        logger.error("No movies found. Please run seed_movies.py first.")
        return
    logger.info("Found %s movies.", len(movies))

    # 3. Generate Reviews
    comments: list[str] = [
        "A classic whodunit structure!",
        "I figured it out halfway through.",
        "Completely baffled me until the end.",
        "The clues were all there, fair play indeed.",
        "A bit unfair with the hidden evidence.",
        "Great atmosphere, but the mystery was weak.",
        "Must watch for any mystery fan.",
    ]

    reviews_created = 0

    for movie in movies:
        for user in users:
            # Create Review
            if not Review.objects.filter(movie=movie, user=user).exists():
                Review.objects.create(
                    movie=movie,
                    user=user,
                    quality=secrets.randbelow(3) + 3,  # Bias towards good movies
                    difficulty=secrets.randbelow(5) + 1,
                    is_fair_play=secrets.choice([True, True, False]),
                    solved=secrets.choice([True, True, False]),
                    comment=secrets.choice(comments),
                )
                reviews_created += 1

    logger.info("Done! Created %s reviews.", reviews_created)
