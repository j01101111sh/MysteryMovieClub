from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse

from movies.models import MysteryTitle, Review, ReviewHelpfulVote
from movies.tests.factories import MovieFactory, ReviewFactory, UserFactory


class ReviewTests(TestCase):
    def setUp(self) -> None:
        self.user, self.upass = UserFactory.create()
        self.uname = self.user.get_username()

        self.movie = MovieFactory.create()
        self.url = reverse("movies:add_review", kwargs={"slug": self.movie.slug})

    def test_review_model_creation(self) -> None:
        """Test that a review can be created and the string representation is correct."""
        review = ReviewFactory.create(user=self.user, movie=self.movie, solved=True)
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
        self.user, _ = UserFactory.create()
        self.movie = MovieFactory.create()
        self.review = ReviewFactory.create(user=self.user, movie=self.movie)
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
        self.user, self.upass = UserFactory.create()
        self.uname = self.user.get_username()
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


class ReviewHelpfulVoteModelTests(TestCase):
    """Unit tests for the ReviewHelpfulVote model."""

    def setUp(self) -> None:
        """Set up test data."""

        self.user1, _ = UserFactory.create()
        self.user2, _ = UserFactory.create()
        self.movie = MysteryTitle.objects.create(
            title="Test Movie",
            slug="test-movie",
            release_year=2023,
        )
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.user1,
            quality=4,
            difficulty=3,
            is_fair_play=True,
            comment="Great mystery!",
        )

    def test_create_helpful_vote(self) -> None:
        """Test creating a helpful vote."""
        vote = ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=True,
        )

        self.assertEqual(vote.review, self.review)
        self.assertEqual(vote.user, self.user2)
        self.assertTrue(vote.is_helpful)

    def test_create_not_helpful_vote(self) -> None:
        """Test creating a not helpful vote."""
        vote = ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=False,
        )

        self.assertFalse(vote.is_helpful)

    def test_string_representation(self) -> None:
        """Test the string representation of a helpful vote."""
        vote = ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=True,
        )

        expected = f"{self.user2} voted helpful on review #{self.review.pk}"
        self.assertEqual(str(vote), expected)

    def test_unique_constraint(self) -> None:
        """Test that a user cannot vote twice on the same review."""
        ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.user2,
            is_helpful=True,
        )

        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            ReviewHelpfulVote.objects.create(
                review=self.review,
                user=self.user2,
                is_helpful=False,
            )


class ReviewHelpfulStatsTests(TestCase):
    """Unit tests for review helpful statistics."""

    def setUp(self) -> None:
        """Set up test data."""
        self.reviewer, _ = UserFactory.create()
        self.voter1, _ = UserFactory.create()
        self.voter2, _ = UserFactory.create()
        self.voter3, _ = UserFactory.create()
        self.movie = MysteryTitle.objects.create(
            title="Test Movie",
            slug="test-movie-stats",
            release_year=2023,
        )
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.reviewer,
            quality=4,
            difficulty=3,
            is_fair_play=True,
            comment="Test review",
        )

    def test_initial_counts_are_zero(self) -> None:
        """Test that initial helpful counts are zero."""
        self.assertEqual(self.review.helpful_count, 0)
        self.assertEqual(self.review.not_helpful_count, 0)
        self.assertEqual(self.review.helpfulness_score, 0.0)

    def test_helpful_count_updates_on_vote(self) -> None:
        """Test that helpful count updates when votes are created."""
        ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter1,
            is_helpful=True,
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 1)
        self.assertEqual(self.review.not_helpful_count, 0)

    def test_not_helpful_count_updates_on_vote(self) -> None:
        """Test that not helpful count updates when votes are created."""
        ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter1,
            is_helpful=False,
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 0)
        self.assertEqual(self.review.not_helpful_count, 1)

    def test_helpfulness_score_calculation(self) -> None:
        """Test the helpfulness score percentage calculation."""
        # 2 helpful, 1 not helpful = 66.67%
        ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter1,
            is_helpful=True,
        )
        ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter2,
            is_helpful=True,
        )
        ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter3,
            is_helpful=False,
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 2)
        self.assertEqual(self.review.not_helpful_count, 1)
        self.assertAlmostEqual(self.review.helpfulness_score, 66.67, places=1)

    def test_counts_update_on_vote_deletion(self) -> None:
        """Test that counts update when a vote is deleted."""
        vote = ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter1,
            is_helpful=True,
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 1)

        vote.delete()

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 0)

    def test_counts_update_on_vote_change(self) -> None:
        """Test that counts update when a vote is changed."""
        vote = ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter1,
            is_helpful=True,
        )

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 1)
        self.assertEqual(self.review.not_helpful_count, 0)

        vote.is_helpful = False
        vote.save()

        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 0)
        self.assertEqual(self.review.not_helpful_count, 1)


class ReviewHelpfulVoteViewTests(TestCase):
    """Unit tests for the review helpful voting views."""

    def setUp(self) -> None:
        """Set up test data."""
        self.reviewer, self.reviewer_password = UserFactory.create()
        self.reviewer_username = self.reviewer.get_username()
        self.voter, self.voter_password = UserFactory.create()
        self.voter_username = self.voter.get_username()

        self.movie = MysteryTitle.objects.create(
            title="Test Movie",
            slug="test-movie-views",
            release_year=2023,
        )
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.reviewer,
            quality=4,
            difficulty=3,
            is_fair_play=True,
            comment="Test review",
        )

    def test_login_required(self) -> None:
        """Test that voting requires authentication."""
        url = reverse("movies:review_helpful_vote", kwargs={"pk": self.review.pk})
        response = self.client.post(url, {"is_helpful": "true"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "/accounts/login/?next=/movies/review/1/helpful/",
        )

    def test_vote_helpful(self) -> None:
        """Test voting that a review is helpful."""
        self.client.login(
            username=self.voter_username,
            password=self.voter_password,
        )

        url = reverse("movies:review_helpful_vote", kwargs={"pk": self.review.pk})
        _ = self.client.post(url, {"is_helpful": "true"})

        self.assertTrue(
            ReviewHelpfulVote.objects.filter(
                review=self.review,
                user=self.voter,
                is_helpful=True,
            ).exists(),
        )

    def test_vote_not_helpful(self) -> None:
        """Test voting that a review is not helpful."""
        self.client.login(
            username=self.voter_username,
            password=self.voter_password,
        )

        url = reverse("movies:review_helpful_vote", kwargs={"pk": self.review.pk})
        _ = self.client.post(url, {"is_helpful": "false"})

        self.assertTrue(
            ReviewHelpfulVote.objects.filter(
                review=self.review,
                user=self.voter,
                is_helpful=False,
            ).exists(),
        )

    def test_cannot_vote_on_own_review(self) -> None:
        """Test that users cannot vote on their own reviews."""
        self.client.login(
            username=self.reviewer_username,
            password=self.reviewer_password,  # Won't work but doesn't matter for this test
        )
        # Need to log in as the reviewer properly
        self.client.force_login(self.reviewer)

        url = reverse("movies:review_helpful_vote", kwargs={"pk": self.review.pk})
        response = self.client.post(url, {"is_helpful": "true"}, follow=True)

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("cannot vote on your own", str(messages[0]))

        self.assertFalse(
            ReviewHelpfulVote.objects.filter(
                review=self.review,
                user=self.reviewer,
            ).exists(),
        )

    def test_toggle_vote_off(self) -> None:
        """Test that voting the same way twice removes the vote."""
        self.client.login(
            username=self.voter_username,
            password=self.voter_password,
        )

        url = reverse("movies:review_helpful_vote", kwargs={"pk": self.review.pk})

        # First vote
        self.client.post(url, {"is_helpful": "true"})
        self.assertEqual(ReviewHelpfulVote.objects.count(), 1)

        # Second vote (same) - should remove
        self.client.post(url, {"is_helpful": "true"})
        self.assertEqual(ReviewHelpfulVote.objects.count(), 0)

    def test_change_vote(self) -> None:
        """Test that voting differently updates the existing vote."""
        self.client.login(
            username=self.voter_username,
            password=self.voter_password,
        )

        url = reverse("movies:review_helpful_vote", kwargs={"pk": self.review.pk})

        # Vote helpful
        self.client.post(url, {"is_helpful": "true"})
        vote = ReviewHelpfulVote.objects.get(review=self.review, user=self.voter)
        self.assertTrue(vote.is_helpful)

        # Change to not helpful
        self.client.post(url, {"is_helpful": "false"})
        vote.refresh_from_db()
        self.assertFalse(vote.is_helpful)
        self.assertEqual(ReviewHelpfulVote.objects.count(), 1)


class ReviewHelpfulSignalTests(TestCase):
    """Unit tests for review helpful voting signals."""

    def setUp(self) -> None:
        """Set up test data."""
        self.reviewer, _ = UserFactory.create()
        self.voter, _ = UserFactory.create()
        self.movie = MysteryTitle.objects.create(
            title="Signal Test Movie",
            slug="signal-test-movie",
            release_year=2023,
        )
        self.review = Review.objects.create(
            movie=self.movie,
            user=self.reviewer,
            quality=4,
            difficulty=3,
            is_fair_play=True,
        )

    def test_vote_creation_logging(self) -> None:
        """Test that creating a helpful vote triggers a log message."""
        with self.assertLogs("movies.signals", level="INFO") as cm:
            ReviewHelpfulVote.objects.create(
                review=self.review,
                user=self.voter,
                is_helpful=True,
            )

            expected_msg = (
                f"Helpful vote created: {self.voter} voted helpful "
                f"on review by {self.reviewer}"
            )
            self.assertTrue(
                any(expected_msg in o for o in cm.output),
                f"Expected log message not found in {cm.output}",
            )

    def test_vote_deletion_logging(self) -> None:
        """Test that deleting a helpful vote triggers a log message."""
        vote = ReviewHelpfulVote.objects.create(
            review=self.review,
            user=self.voter,
            is_helpful=True,
        )

        with self.assertLogs("movies.signals", level="INFO") as cm:
            vote.delete()

            expected_msg = (
                f"Helpful vote removed: {self.voter} removed vote "
                f"from review by {self.reviewer}"
            )
            self.assertTrue(
                any(expected_msg in o for o in cm.output),
                f"Expected log message not found in {cm.output}",
            )
