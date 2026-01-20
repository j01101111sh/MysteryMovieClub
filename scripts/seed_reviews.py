import logging
import secrets
from typing import Any

from django.contrib.auth import get_user_model

# Local imports
from movies.models import MysteryTitle, Review

logger = logging.getLogger(__name__)


def create_reviews() -> None:
    """
    Seeds the database with users and reviews.
    Requires Movies to be seeded first.
    """
    User = get_user_model()

    logger.info("Seeding users and reviews...")

    # 1. Create Sample Users
    num_users = 10
    user_data: list[dict[str, str]] = [
        {
            "username": (uname := f"user_{secrets.token_hex(8)}"),
            "email": f"{uname}@example.com",
            "password": secrets.token_urlsafe(16),
        }
        for _ in range(num_users)
    ]

    user_objects: list[Any] = []
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={"email": data["email"]},
        )
        if created:
            user.set_password(data["password"])
            user.save()
            logger.info("Created user: %s", user.username)
        else:
            logger.info("User already exists: %s", user.username)
        user_objects.append(user)

    logger.info("Verified %s users.", len(user_objects))

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
        for user in user_objects:
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
