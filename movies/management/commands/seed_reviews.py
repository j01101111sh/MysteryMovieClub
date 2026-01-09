import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from movies.models import MysteryTitle, Review


class Command(BaseCommand):
    help = "Seeds the database with 2 reviews per movie from distinct users"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # 1. Create two dedicated reviewer users
        # We use get_or_create to make the script idempotent
        user_a, created_a = User.objects.get_or_create(
            username="reviewer_poirot", defaults={"email": "poirot@example.com"}
        )
        if created_a:
            user_a.set_password("password123")
            user_a.save()
            self.stdout.write(f"Created user: {user_a.username}")

        user_b, created_b = User.objects.get_or_create(
            username="reviewer_marple", defaults={"email": "marple@example.com"}
        )
        if created_b:
            user_b.set_password("password123")
            user_b.save()
            self.stdout.write(f"Created user: {user_b.username}")

        users = [user_a, user_b]

        # 2. Fetch all movies
        movies = MysteryTitle.objects.all()
        if not movies.exists():
            self.stdout.write(
                self.style.WARNING(
                    "No movies found. Please run 'python manage.py seed_imdb_mysteries' first."
                )
            )
            return

        # 3. Create reviews
        reviews_created = 0

        comments_list = [
            "A twisting plot that kept me guessing until the end.",
            "The clues were there, but I missed them completely!",
            "A classic whodunit structure, very well executed.",
            "I felt the solution came a bit out of nowhere.",
            "Fair play strictly speaking, but very obscure logic.",
            "Masterpiece of the genre.",
            "Good atmosphere, but the mystery was weak.",
            "Highly recommended for fans of the genre.",
            "Solvable if you pay close attention to the dialogue.",
            "A bit slow in the middle, but the payoff is worth it.",
        ]

        self.stdout.write(f"Seeding reviews for {movies.count()} movies...")

        for movie in movies:
            for user in users:
                # Check uniqueness constraint to prevent errors on re-runs
                if not Review.objects.filter(movie=movie, user=user).exists():
                    Review.objects.create(
                        movie=movie,
                        user=user,
                        quality=random.randint(3, 5),  # Generally positive for our club
                        difficulty=random.randint(1, 5),
                        is_fair_play=random.choice(
                            [True, True, False]
                        ),  # Bias towards True
                        comment=random.choice(comments_list),
                    )
                    reviews_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {reviews_created} reviews.")
        )
