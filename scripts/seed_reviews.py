# scripts/seed_reviews.py
import os
import secrets
import sys
from pathlib import Path
from typing import Any

import django
from django.utils.text import slugify

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from movies.models import MysteryTitle, Review, Tag, TagVote  # noqa: E402

User = get_user_model()

gen = secrets.SystemRandom()


def main() -> None:
    print("Seeding reviews and tags...")

    # 1. Create/Ensure Tags Exist
    tag_names = [
        # Sub-genres
        "Whodunit",
        "Howcatchem",
        "Locked Room",
        "Cozy Mystery",
        "Noir",
        "Neo-Noir",
        "Police Procedural",
        "Hardboiled",
        "Giallo",
        "Historical Mystery",
        # Tropes & Plot Elements
        "Unreliable Narrator",
        "Plot Twist",
        "Red Herring",
        "Cold Case",
        "Serial Killer",
        "Amateur Sleuth",
        "Private Investigator",
        "Courtroom Drama",
        "Supernatural Elements",
        "Heist",
        # Tone & Style
        "Dark",
        "Humorous",
        "Campy",
        "Tense",
        "Slow Burn",
        "Fast-Paced",
        "Atmospheric",
        "Brain Burner",
    ]

    print(f"Ensuring {len(tag_names)} tags exist...")
    all_tags = []
    for name in tag_names:
        slug = slugify(name)
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
        all_tags.append(tag)

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
        user_objects.append(user)

    print(f"Verified {len(user_objects)} users.")

    # 3. Fetch Movies
    movies = MysteryTitle.objects.all()
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
            chosen_tags = secrets.SystemRandom.sample(gen, all_tags, num_tags)

            for tag in chosen_tags:
                _, created = TagVote.objects.get_or_create(
                    movie=movie,
                    user=user,
                    tag=tag,
                )
                if created:
                    tag_votes_created += 1

    print(f"Done! Created {reviews_created} reviews and {tag_votes_created} tag votes.")


if __name__ == "__main__":
    main()
