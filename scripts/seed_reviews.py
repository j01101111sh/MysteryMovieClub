import logging
import secrets

from django.contrib.auth import get_user_model
from django.db.models import Q

from movies.models import MysteryTitle, Review, ReviewHelpfulVote

logger = logging.getLogger(__name__)


def create_reviews() -> None:
    """
    Seeds the database with reviews and helpful votes.

    Creates reviews from various users and generates realistic
    helpful/not helpful votes to simulate community engagement.
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
    review_objects = []

    for movie in movies:
        for user in users:
            # Create Review - only some users review each movie (50% chance)
            if (
                not Review.objects.filter(movie=movie, user=user).exists()
                and secrets.randbelow(2) == 0
            ):  # 50% chance to review
                review = Review.objects.create(
                    movie=movie,
                    user=user,
                    quality=secrets.randbelow(3) + 3,  # 3-5, bias towards good
                    difficulty=secrets.randbelow(5) + 1,  # 1-5, even distribution
                    is_fair_play=secrets.choice([True, True, False]),
                    solved=secrets.choice([True, True, False]),
                    comment=secrets.choice(comments),
                )
                reviews_created += 1
                review_objects.append(review)

    logger.info("Done! Created %s reviews.", reviews_created)

    # 4. Generate Helpful Votes
    logger.info("Seeding helpful votes for reviews...")

    helpful_votes_created = 0
    gen = secrets.SystemRandom()

    for review in review_objects:
        # Determine how many users will vote on this review
        # More likely that popular/early reviews get more votes
        # Base: 20-80% of users might vote on any given review
        vote_percentage = gen.uniform(0.2, 0.8)
        num_voters = int(len(users) * vote_percentage)

        # Select random voters (excluding the review author)
        potential_voters = [u for u in users if u != review.user]
        voters = gen.sample(
            potential_voters,
            min(num_voters, len(potential_voters)),
        )

        for voter in voters:
            # Don't create duplicate votes
            if ReviewHelpfulVote.objects.filter(
                review=review,
                user=voter,
            ).exists():
                continue

            # Higher quality reviews are more likely to be marked helpful
            # Adjust probability based on review quality
            quality_factor = (review.quality - 1) / 4  # Normalize to 0-1
            is_helpful_adjusted = gen.random() < (0.5 + quality_factor * 0.4)

            ReviewHelpfulVote.objects.create(
                review=review,
                user=voter,
                is_helpful=is_helpful_adjusted,
            )
            helpful_votes_created += 1

    logger.info("Done! Created %s helpful votes.", helpful_votes_created)

    # 5. Log summary statistics
    reviews_with_votes = Review.objects.filter(
        Q(helpful_count__gt=0) | Q(not_helpful_count__gt=0),
    ).count()

    avg_votes_per_review = (
        helpful_votes_created / reviews_created if reviews_created > 0 else 0
    )

    logger.info("Summary:")
    logger.info("  - Total reviews: %s", reviews_created)
    logger.info("  - Total helpful votes: %s", helpful_votes_created)
    logger.info("  - Reviews with votes: %s", reviews_with_votes)
    logger.info("  - Avg votes per review: %.2f", avg_votes_per_review)
