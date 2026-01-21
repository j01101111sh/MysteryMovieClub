import secrets

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse

from movies.models import MysteryTitle, Review


class ReviewTests(TestCase):
    def setUp(self) -> None:
        self.uname = f"user_{secrets.token_hex(4)}"
        self.upass = secrets.token_urlsafe(16)

        self.user = get_user_model().objects.create_user(  # type: ignore
            username=self.uname,
            password=self.upass,
        )
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            media_type=MysteryTitle.MediaType.MOVIE,
        )
        self.url = reverse("movies:add_review", kwargs={"slug": self.movie.slug})

    def test_review_model_creation(self) -> None:
        """Test that a review can be created and the string representation is correct."""
        review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
            solved=True,
            comment="Great movie!",
        )
        self.assertEqual(str(review), f"{self.user}'s review of {self.movie}")
        self.assertEqual(Review.objects.count(), 1)
        self.assertTrue(review.solved)

    def test_review_model_solved_default(self) -> None:
        """Test that the solved field defaults to False."""
        review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
        )
        self.assertFalse(review.solved)

    def test_unique_review_constraint(self) -> None:
        """Test that a user cannot review the same movie twice."""
        Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
        )
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                movie=self.movie,
                user=self.user,
                quality=1,
                difficulty=1,
                is_fair_play=False,
            )

    def test_create_view_login_required(self) -> None:
        """Test that the review creation view requires login."""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_create_view_get(self) -> None:
        """Test that the review creation page loads for a logged-in user."""
        self.client.login(username=self.uname, password=self.upass)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/review_form.html")
        self.assertEqual(response.context["movie"], self.movie)

    def test_create_view_post_success(self) -> None:
        """Test that a valid review form submission creates a review."""
        self.client.login(username=self.uname, password=self.upass)
        data = {
            "quality": 5,
            "difficulty": 4,
            "is_fair_play": True,
            "solved": True,
            "comment": "Loved it",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.movie.get_absolute_url())
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        if review:
            self.assertEqual(review.quality, 5)
            self.assertEqual(review.user, self.user)
            self.assertTrue(review.solved)
        else:
            raise AssertionError

    def test_create_view_post_duplicate(self) -> None:
        """Test that posting a duplicate review redirects with a warning message."""
        # Create initial review
        Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=3,
            difficulty=3,
            is_fair_play=False,
        )

        self.client.login(username=self.uname, password=self.upass)
        data = {
            "quality": 5,
            "difficulty": 4,
            "is_fair_play": True,
            "comment": "Changed my mind",
        }
        # The view catches IntegrityError and redirects
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(response, self.movie.get_absolute_url())

        # Check for message
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have already reviewed this movie.")

        # Ensure count is still 1 and data hasn't changed
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        if review:
            self.assertEqual(review.quality, 3)
        else:
            raise AssertionError

    def test_detail_view_context_has_reviewed(self) -> None:
        """Test that the 'has_reviewed' context variable is set correctly."""
        detail_url = self.movie.get_absolute_url()

        # Not logged in
        response = self.client.get(detail_url)
        self.assertNotIn("has_reviewed", response.context)

        # Logged in, no review
        self.client.login(username=self.uname, password=self.upass)
        response = self.client.get(detail_url)
        self.assertFalse(response.context["has_reviewed"])

        # Logged in, with review
        Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=4,
            difficulty=4,
            is_fair_play=True,
        )
        response = self.client.get(detail_url)
        self.assertTrue(response.context["has_reviewed"])

    def test_review_creation_logging(self) -> None:
        """Test that creating a review triggers a log message."""
        with self.assertLogs("movies.signals", level="INFO") as cm:
            Review.objects.create(
                movie=self.movie,
                user=self.user,
                quality=5,
                difficulty=3,
                is_fair_play=True,
                comment="Log Test Review",
            )

            # Verify the log message exists and contains the string representation
            expected_msg = f"Review created: {self.user} for {self.movie.slug}"
            self.assertTrue(any(expected_msg in o for o in cm.output))


class ReviewListViewTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(  # type: ignore
            username=f"user_{secrets.token_hex(4)}",
            password=secrets.token_urlsafe(16),
        )
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            media_type=MysteryTitle.MediaType.MOVIE,
        )
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
            comment="Great movie!",
        )
        self.url = reverse("movies:review_list", kwargs={"slug": self.movie.slug})

    def test_review_list_status_code(self) -> None:
        """Test that the review list page returns a 200 OK status code."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_review_list_context(self) -> None:
        """Test that the review list page context contains the reviews and movie."""
        response = self.client.get(self.url)
        self.assertIn(self.review, response.context["reviews"])
        self.assertEqual(response.context["movie"], self.movie)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    },
)
class ReviewCacheTests(TestCase):
    def setUp(self) -> None:
        self.uname = f"user_{secrets.token_hex(4)}"
        self.upass = secrets.token_urlsafe(16)

        self.user = get_user_model().objects.create_user(  # type: ignore
            username=self.uname,
            password=self.upass,
        )
        self.movie = MysteryTitle.objects.create(
            title="Glass Onion",
            slug="glass-onion",
            release_year=2022,
            media_type=MysteryTitle.MediaType.MOVIE,
        )
        # Reconstruct the key used in the template: {% cache 900 heatmap movie.pk %}
        self.cache_key = make_template_fragment_key("heatmap", [self.movie.pk])

    def tearDown(self) -> None:  # noqa
        # Clear cache after every test to ensure isolation
        cache.clear()

    def test_heatmap_cache_invalidation_on_create(self) -> None:
        """Test that creating a review invalidates the heatmap cache."""
        # 1. Simulate the cache being populated (as if the template just rendered)
        cache.set(self.cache_key, "<div>Cached Heatmap HTML</div>")

        # Verify it exists
        self.assertIsNotNone(cache.get(self.cache_key))

        # 2. Create a review (triggers the post_save signal)
        Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
        )

        # 3. Verify the cache key is now gone
        self.assertIsNone(cache.get(self.cache_key))

    def test_heatmap_cache_invalidation_on_delete(self) -> None:
        """Test that deleting a review invalidates the heatmap cache."""
        review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
        )

        # 1. Populate cache
        cache.set(self.cache_key, "<div>Cached Heatmap HTML</div>")
        self.assertIsNotNone(cache.get(self.cache_key))

        # 2. Delete the review (triggers the post_delete signal)
        review.delete()

        # 3. Verify the cache key is now gone
        self.assertIsNone(cache.get(self.cache_key))
