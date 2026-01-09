# scripts/seed_reviews.py
import os
import random
import sys
from pathlib import Path

import django

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from movies.models import MysteryTitle, Review  # noqa: E402

User = get_user_model()


def main():
    print("Seeding reviews...")

    # 1. Create Sample Users
    reviewers = [
        {
            "username": "alice_detective",
            "email": "alice@example.com",
            "password": "password123",
        },
        {"username": "bob_noir", "email": "bob@example.com", "password": "password123"},
        {
            "username": "charlie_clue",
            "email": "charlie@example.com",
            "password": "password123",
        },
    ]

    user_objects = []
    for reviewer in reviewers:
        user, created = User.objects.get_or_create(
            username=reviewer["username"], defaults={"email": reviewer["email"]}
        )
        if created:
            user.set_password(reviewer["password"])
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User already exists: {user.username}")
        user_objects.append(user)

    # 2. Fetch Movies
    movies = list(MysteryTitle.objects.all())
    if not movies:
        print("No movies found. Please run seed_imdb_mysteries.py first.")
        return
    else:
        print(f"Found {len(movies)}.")

    # 3. Generate Reviews
    # Comments to pick from randomly
    comments = [
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
        # Randomly decide how many reviews this movie gets (0 to 3)
        num_reviews = 2

        # Pick random users to review this movie
        selected_users = random.sample(user_objects, num_reviews)

        for user in selected_users:
            # Check if review already exists to avoid unique constraint error
            if not Review.objects.filter(movie=movie, user=user).exists():
                _ = Review.objects.create(
                    movie=movie,
                    user=user,
                    quality=random.randint(3, 5),  # Bias towards good movies
                    difficulty=random.randint(1, 5),
                    is_fair_play=random.choice(
                        [True, True, False]
                    ),  # Bias towards True
                    comment=random.choice(comments),
                )
                reviews_created += 1

    print(f"Done! Created {reviews_created} new reviews.")


if __name__ == "__main__":
    main()
