from django.test import TestCase

from movies.models import MysteryTitle
from movies.tests.factories import MovieFactory, ReviewFactory, UserFactory


class FactoryVerificationTests(TestCase):
    """
    Unit tests to verify that the test factories produce valid, persisted objects.
    """

    def test_user_factory_creates_valid_user(self) -> None:
        """
        Test that UserFactory creates a user with the correct username and password.
        """
        test_username = "testuser"
        user, password = UserFactory.create(username=test_username)

        self.assertEqual(user.get_username(), test_username)
        self.assertTrue(user.check_password(password))
        self.assertIsNotNone(user.pk)

    def test_user_factory_random_defaults(self) -> None:
        """
        Test that UserFactory generates unique defaults when no args are provided.
        """
        user1, _ = UserFactory.create()
        user2, _ = UserFactory.create()

        self.assertNotEqual(user1.get_username(), user2.get_username())
        self.assertNotEqual(user1.pk, user2.pk)

    def test_movie_factory_creates_movie(self) -> None:
        """
        Test that MovieFactory creates a MysteryTitle with defaults.
        """
        movie = MovieFactory.create()

        self.assertIsInstance(movie, MysteryTitle)
        self.assertTrue(movie.title.startswith("Mystery"))
        self.assertIsNotNone(movie.pk)

    def test_movie_factory_overrides(self) -> None:
        """
        Test that arguments passed to MovieFactory override defaults.
        """
        movie = MovieFactory.create(title="Knives Out", release_year=2019)

        self.assertEqual(movie.title, "Knives Out")
        self.assertEqual(movie.release_year, 2019)

    def test_review_factory_links_correctly(self) -> None:
        """
        Test that ReviewFactory correctly associates user and movie.
        """
        user, _ = UserFactory.create()
        movie = MovieFactory.create()
        review_quality = 5

        review = ReviewFactory.create(user=user, movie=movie, quality=review_quality)

        self.assertEqual(review.user, user)
        self.assertEqual(review.movie, movie)
        self.assertEqual(review.quality, review_quality)
        self.assertIsNotNone(review.pk)
        self.assertIsNotNone(review.pk)
