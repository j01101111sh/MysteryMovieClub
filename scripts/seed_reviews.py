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

from movies.models import MysteryTitle, Review  # noqa: E402

User = get_user_model()


def main() -> None:
    print("Seeding reviews...")

    # 1. Create Sample Users
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
    movies = MysteryTitle.objects.all()
    if not movies:
        print("No movies found. Please run seed_imdb_mysteries.py first.")
        return
    else:
        print(f"Found {len(movies)}.")

    # 3. Generate Reviews
    # Comments to pick from randomly
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
            # Check if review already exists to avoid unique constraint error
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

    print(f"Done! Created {reviews_created} new reviews.")


if __name__ == "__main__":
    main()
