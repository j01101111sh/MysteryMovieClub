# scripts/seed_reviews.py
import os
import secrets
import sys
from pathlib import Path
from typing import Any

import django

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from movies.models import (  # noqa: E402
    Collection,
    CollectionItem,
    MysteryTitle,
    Review,
    Tag,
    TagVote,
    WatchListEntry,
)

User = get_user_model()

gen = secrets.SystemRandom()


def main() -> None:
    print("Seeding reviews and tags...")

    # 1. Create/Ensure Tags Exist
    all_tags = list(Tag.objects.all())
    if not all_tags:
        print("No tags found in the database. Please run seed_tags.py first.")
        return
    print(f"Found {len(all_tags)} tags to use for voting.")

    # 2. Create Sample Users
    num_reviews = 10
    reviewers: list[dict[str, str]] = [
        {
            "username": (uname := f"user_{secrets.token_hex(8)}"),
            "email": f"{uname}@example.com",
            "password": secrets.token_urlsafe(16),
        }
        for _ in range(num_reviews)
    ]

    user_objects: list[Any] = []
    for reviewer in reviewers:
        user, created = User.objects.get_or_create(
            username=reviewer["username"],
            defaults={"email": reviewer["email"]},
        )
        if created:
            user.set_password(reviewer["password"])
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User already exists: {user.username}")
        user_objects.append(user)

    print(f"Verified {len(user_objects)} users.")

    # 3. Fetch Movies
    # Convert to list for random sampling later
    movies = list(MysteryTitle.objects.all())
    if not movies:
        print("No movies found. Please run seed_movies.py first.")
        return
    print(f"Found {len(movies)} movies.")

    # 4. Generate Reviews and Tag Votes
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
    tag_votes_created = 0
    watchlist_entries_created = 0

    for movie in movies:
        for user in user_objects:
            # Create Review
            if not Review.objects.filter(movie=movie, user=user).exists():
                _ = Review.objects.create(
                    movie=movie,
                    user=user,
                    quality=secrets.randbelow(3) + 3,  # Bias towards good movies
                    difficulty=secrets.randbelow(5) + 1,
                    is_fair_play=secrets.choice([True, True, False]),
                    solved=secrets.choice([True, True, False]),
                    comment=secrets.choice(comments),
                )
                reviews_created += 1

            # Create Tag Votes
            # Randomly assign 1 to 4 tags per user per movie to simulate activity
            # Use random.sample to pick unique tags from the list
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

            # Create Watchlist Entry
            # Randomly decide to add to watchlist (30% chance)
            if secrets.randbelow(10) < 3:
                _, created = WatchListEntry.objects.get_or_create(
                    user=user,
                    movie=movie,
                )
                if created:
                    watchlist_entries_created += 1

    # 5. Generate Collections
    print("Seeding collections...")
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

    for user in user_objects:
        # Create 2-4 collections per user
        num_collections = secrets.randbelow(2) + 2
        if num_collections == 0:
            continue

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

    print(
        f"Done! Created {reviews_created} reviews, {tag_votes_created} tag votes, "
        f"{watchlist_entries_created} watchlist entries, "
        f"{collections_created} collections, and {collection_items_created} collection items.",
    )


if __name__ == "__main__":
    main()
