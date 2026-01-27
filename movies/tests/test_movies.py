from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from config.tests.factories import (
    DirectorFactory,
    MovieFactory,
    ReviewFactory,
    UserFactory,
)
from movies.models import Director, MysteryTitle, Review, Series


class MysteryTitleModelTests(TestCase):
    def setUp(self) -> None:
        self.director = DirectorFactory.create(
            name="Rian Johnson",
        )
        self.series = Series.objects.create(name="Benoit Blanc")
        self.movie = MovieFactory.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            series=self.series,
            director=self.director,
        )

    def test_string_representation(self) -> None:
        """Test the model's string representation uses Title (Year)."""
        self.assertEqual(str(self.movie), "Knives Out (2019)")

    def test_get_absolute_url(self) -> None:
        """Test that get_absolute_url generates the correct path."""
        expected_url = reverse("movies:detail", kwargs={"slug": self.movie.slug})
        self.assertEqual(self.movie.get_absolute_url(), expected_url)
        self.assertEqual(self.movie.get_absolute_url(), "/movies/knives-out-2019/")

    def test_default_values(self) -> None:
        """Test that default values for scores and flags are set correctly."""
        self.assertTrue(self.movie.is_fair_play_candidate)
        self.assertEqual(self.movie.avg_quality, 0.0)
        self.assertEqual(self.movie.avg_difficulty, 0.0)
        self.assertEqual(self.movie.fair_play_consensus, 0.0)

    def test_ordering(self) -> None:
        """Test that movies are ordered by release_year descending, then title."""
        m_older = MovieFactory.create(
            release_year=2018,
        )
        m_newer = MovieFactory.create(
            release_year=2020,
        )
        m_same_year = MovieFactory.create(
            title="Aaa",
            release_year=2019,
        )
        expected = [m_newer, m_same_year, self.movie, m_older]
        self.assertEqual(list(MysteryTitle.objects.all()), expected)

    def test_slug_uniqueness(self) -> None:
        """Test that duplicate slugs raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            _ = MovieFactory.create(
                slug=self.movie.slug,
            )

    def test_series_relationship(self) -> None:
        """Test the foreign key relationship to the Series model."""
        self.assertEqual(self.movie.series, self.series)
        self.assertIn(self.movie, self.series.movies.all())

    def test_movie_creation_logging(self) -> None:
        """Test that creating a movie triggers a log message."""
        # Use assertLogs to catch logs from the movies.models logger
        with self.assertLogs("movies.signals", level="INFO") as cm:
            _ = MovieFactory.create(
                title="Log Test Movie",
                slug="log-test-movie",
            )
            # Verify the log message exists
            self.assertTrue(
                any("Movie created: log-test-movie" in o for o in cm.output),
            )


class MysteryViewTests(TestCase):
    def setUp(self) -> None:
        self.director1 = Director.objects.create(
            name="Rian Johnson",
            slug="rian-johnson",
        )
        self.movie1 = MovieFactory.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            media_type=MysteryTitle.MediaType.MOVIE,
            description="Whodunit description",
            director=self.director1,
        )

        self.director2 = Director.objects.create(
            name="Steven Moffat",
            slug="steven-moffat",
        )
        self.movie2 = MovieFactory.create(
            title="Sherlock",
            slug="sherlock-2010",
            release_year=2010,
            media_type=MysteryTitle.MediaType.TV_SHOW,
            director=self.director2,
        )

    def test_home_page_status_code(self) -> None:
        """Test that the home page returns a 200 OK status code."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self) -> None:
        """Test that the home page uses the correct templates."""
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "movies/movie_list.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_content(self) -> None:
        """Test that the list view context contains our movies and director."""
        response = self.client.get(reverse("home"))
        # Check for movie titles
        self.assertContains(response, "Knives Out")
        self.assertContains(response, "Sherlock")
        # Check that movies are in context
        self.assertIn(self.movie1, response.context["movies"])
        self.assertIn(self.movie2, response.context["movies"])
        # Check for director names
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Steven Moffat")

    def test_detail_page_status_code(self) -> None:
        """Test that a valid mystery detail page returns a 200 OK status code."""
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_page_template(self) -> None:
        """Test that the mystery detail page uses the correct template."""
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/mystery_detail.html")

    def test_detail_page_content(self) -> None:
        """Test that the detail page displays the correct movie information."""
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Knives Out")
        self.assertContains(response, "2019")
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Whodunit description")
        self.assertContains(response, "Movie")

    def test_detail_page_404(self) -> None:
        """Test that requesting a non-existent mystery slug returns a 404 error."""
        url = reverse("movies:detail", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_page_reviews_context(self) -> None:
        """Test that recent reviews are included in the detail page context."""
        user, _ = UserFactory.create()
        _ = ReviewFactory.create(
            movie=self.movie1,
            user=user,
        )
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertIn("recent_reviews", response.context)
        self.assertEqual(len(response.context["recent_reviews"]), 1)
        self.assertEqual(response.context["total_reviews_count"], 1)

    def test_home_page_empty_list(self) -> None:
        """Test that the home page handles an empty database gracefully."""
        MysteryTitle.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["movies"]), [])

    def test_pagination(self) -> None:
        """Test that the movie list is paginated."""
        # Create enough movies to trigger pagination
        for _ in range(25):
            _ = MovieFactory.create()

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(
            len(response.context["movies"]),
            response.context["paginator"].per_page,
        )
        self.assertGreater(response.context["paginator"].num_pages, 1)

    def test_search_logging(self) -> None:
        """Test that searching triggers an INFO log message."""
        # assertLogs acts as a context manager to capture logs
        with self.assertLogs("movies.managers", level="INFO") as cm:
            self.client.get(reverse("home"), {"q": "Knives"})

            # Verify that our specific message appears in the captured output
            self.assertTrue(
                any("Search query received: Knives" in o for o in cm.output),
            )

    def test_search_pagination(self) -> None:
        """Test that the second page of search results works and preserves the query."""
        # Create enough movies to trigger pagination (15 per page)
        # Create 20 "Noir" movies which should match the search
        for i in range(20):
            _ = MovieFactory.create(
                title=f"Noir Movie {i}",
                slug=f"noir-movie-{i}",
                release_year=2020,
                description="Dark and stormy",
            )
        # Create 5 "Comedy" movies (should be excluded)
        for i in range(5):
            _ = MovieFactory.create(
                title=f"Comedy Movie {i}",
                slug=f"comedy-movie-{i}",
                release_year=2020,
                description="Laughs",
            )

        # 1. Test Page 1 of Search
        response_p1 = self.client.get(reverse("home"), {"q": "Noir"})
        self.assertEqual(response_p1.status_code, 200)
        self.assertEqual(len(response_p1.context["movies"]), 15)
        self.assertTrue(response_p1.context["is_paginated"])
        self.assertEqual(response_p1.context["search_query"], "Noir")

        # 2. Test Page 2 of Search
        response_p2 = self.client.get(reverse("home"), {"q": "Noir", "page": "2"})
        self.assertEqual(response_p2.status_code, 200)
        # Should have the remaining 5 Noir movies
        self.assertEqual(len(response_p2.context["movies"]), 5)

        # Verify we only got Noir movies on page 2
        for movie in response_p2.context["movies"]:
            self.assertIn("Noir", movie.title)

        # Verify query is still in context
        self.assertEqual(response_p2.context["search_query"], "Noir")


class MysteryTitleStatsTests(TestCase):
    def setUp(self) -> None:
        self.user1, _ = UserFactory.create()
        self.user2, _ = UserFactory.create()

        self.movie = MovieFactory.create(
            title="Stats Movie",
            slug="stats-movie",
            release_year=2020,
        )

    def test_stats_calculation_and_signals(self) -> None:
        """Test that stats are updated when reviews are created, updated, or deleted."""
        # Initial state
        self.assertEqual(self.movie.avg_quality, 0.0)
        self.assertEqual(self.movie.avg_difficulty, 0.0)
        self.assertEqual(self.movie.fair_play_consensus, 0.0)

        # Add first review
        _ = ReviewFactory.create(
            movie=self.movie,
            user=self.user1,
            quality=4,
            difficulty=2,
            is_fair_play=True,
        )

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.avg_quality, 4.0)
        self.assertEqual(self.movie.avg_difficulty, 2.0)
        self.assertEqual(self.movie.fair_play_consensus, 100.0)

        # Add second review
        review2 = ReviewFactory.create(
            movie=self.movie,
            user=self.user2,
            quality=2,
            difficulty=4,
            is_fair_play=False,
        )

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.avg_quality, 3.0)
        self.assertEqual(self.movie.avg_difficulty, 3.0)
        self.assertEqual(self.movie.fair_play_consensus, 50.0)

        # Update second review
        review2.quality = 5
        review2.save()

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.avg_quality, 4.5)  # (4+5)/2

        # Delete second review
        review2.delete()

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.avg_quality, 4.0)
        self.assertEqual(self.movie.fair_play_consensus, 100.0)

        # Delete all reviews
        for review in Review.objects.filter(movie=self.movie):
            review.delete()

        self.movie.refresh_from_db()
        self.assertEqual(self.movie.avg_quality, 0.0)
        self.assertEqual(self.movie.avg_difficulty, 0.0)
        self.assertEqual(self.movie.fair_play_consensus, 0.0)
