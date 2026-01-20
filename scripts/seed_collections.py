import logging
import secrets

from django.contrib.auth import get_user_model

# Local imports
from movies.models import Collection, CollectionItem, MysteryTitle

logger = logging.getLogger(__name__)


def create_collections() -> None:
    """
    Seeds the database with collections and collection items.
    Requires Users and Movies to be seeded first.
    """
    User = get_user_model()
    gen = secrets.SystemRandom()

    logger.info("Seeding collections...")

    # 1. Fetch Dependencies
    movies = list(MysteryTitle.objects.all())
    if not movies:
        logger.error("No movies found. Please run seed_movies.py first.")
        return

    users = list(User.objects.filter(is_superuser=False))
    if not users:
        logger.warning(
            "No standard users found. Run seed_reviews.py to generate users.",
        )
        users = list(User.objects.all())

    if not users:
        logger.error("No users found. Please run seed_reviews.py first.")
        return

    # 2. Generate Collections
    collections_created = 0
    collection_items_created = 0

    collection_templates = [
        ("Essentials", "Must watch mystery movies."),
        ("Mind Benders", "Movies that will twist your brain."),
        ("Cozy Mysteries", "Perfect for a rainy Sunday."),
        ("Noir Nights", "Dark, gritty, and cynical."),
        ("Whodunits", "Can you guess the killer?"),
        ("Hidden Gems", "Underrated mysteries you might have missed."),
    ]

    for user in users:
        # Create 2-4 collections per user
        num_collections = secrets.randbelow(3) + 2

        chosen_templates = gen.sample(collection_templates, num_collections)

        for title, description in chosen_templates:
            collection, created = Collection.objects.get_or_create(
                user=user,
                name=title,
                defaults={
                    "description": description,
                    "is_public": secrets.choice([True, True, False]),
                },
            )

            if created:
                collections_created += 1

                # Add 3-10 random movies to the collection
                num_items = secrets.randbelow(8) + 3
                chosen_movies = gen.sample(movies, min(num_items, len(movies)))

                for idx, movie in enumerate(chosen_movies):
                    CollectionItem.objects.create(
                        collection=collection,
                        movie=movie,
                        order=idx,
                        note=secrets.choice(
                            ["", "Highly recommended.", "Great plot.", "A classic."],
                        ),
                    )
                    collection_items_created += 1

    logger.info(
        "Done! Created %s collections and %s collection items.",
        collections_created,
        collection_items_created,
    )
