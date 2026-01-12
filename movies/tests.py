import secrets

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from movies.models import Director, MysteryTitle, Review, Series


class MysteryTitleModelTests(TestCase):
    def setUp(self):
        self.director = Director.objects.create(
            name="Rian Johnson", slug="rian-johnson"
        )
        self.series = Series.objects.create(name="Benoit Blanc", slug="benoit-blanc")
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            description="A detective investigates...",
            media_type=MysteryTitle.MediaType.MOVIE,
            series=self.series,
            director=self.director,
        )

    def test_string_representation(self):
        """Test the model's string representation uses Title (Year)."""
        self.assertEqual(str(self.movie), "Knives Out (2019)")

    def test_get_absolute_url(self):
        """Test that get_absolute_url generates the correct path."""
        expected_url = reverse("movies:detail", kwargs={"slug": self.movie.slug})
        self.assertEqual(self.movie.get_absolute_url(), expected_url)
        self.assertEqual(self.movie.get_absolute_url(), "/movies/knives-out-2019/")

    def test_default_values(self):
        """Test that default values for scores and flags are set correctly."""
        self.assertTrue(self.movie.is_fair_play_candidate)
        self.assertEqual(self.movie.avg_quality, 0.0)
        self.assertEqual(self.movie.avg_difficulty, 0.0)
        self.assertEqual(self.movie.fair_play_consensus, 0.0)

    def test_ordering(self):
        """Test that movies are ordered by release_year descending, then title."""
        m_older = MysteryTitle.objects.create(
            title="A Older", slug="older", release_year=2018
        )
        m_newer = MysteryTitle.objects.create(
            title="Z Newer", slug="newer", release_year=2020
        )
        m_same_year = MysteryTitle.objects.create(
            title="A Same Year", slug="same-year", release_year=2019
        )
        expected = [m_newer, m_same_year, self.movie, m_older]
        self.assertEqual(list(MysteryTitle.objects.all()), expected)

    def test_slug_uniqueness(self):
        """Test that duplicate slugs raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            MysteryTitle.objects.create(
                title="Dup", slug=self.movie.slug, release_year=2020
            )

    def test_series_relationship(self):
        """Test the foreign key relationship to the Series model."""
        self.assertEqual(self.movie.series, self.series)
        self.assertIn(self.movie, self.series.movies.all())


class DirectorModelTests(TestCase):
    def setUp(self):
        self.director = Director.objects.create(
            name="Alfred Hitchcock", slug="alfred-hitchcock"
        )

    def test_string_representation(self):
        self.assertEqual(str(self.director), "Alfred Hitchcock")

    def test_get_absolute_url(self):
        expected_url = reverse(
            "movies:director_detail", kwargs={"slug": self.director.slug}
        )
        self.assertEqual(self.director.get_absolute_url(), expected_url)

    def test_slug_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Director.objects.create(name="Hitchcock", slug="alfred-hitchcock")

    def test_name_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Director.objects.create(name="Alfred Hitchcock", slug="hitchcock")


class SeriesModelTests(TestCase):
    def setUp(self):
        self.series = Series.objects.create(name="Benoit Blanc", slug="benoit-blanc")

    def test_string_representation(self):
        self.assertEqual(str(self.series), "Benoit Blanc")

    def test_get_absolute_url(self):
        expected_url = reverse(
            "movies:series_detail", kwargs={"slug": self.series.slug}
        )
        self.assertEqual(self.series.get_absolute_url(), expected_url)

    def test_slug_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Series.objects.create(name="Blanc", slug="benoit-blanc")

    def test_name_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Series.objects.create(name="Benoit Blanc", slug="blanc")


class BaseTemplateTests(TestCase):
    def test_favicon_present(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<link rel="icon"')
        self.assertContains(
            response,
            "data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E🕵️%3C/text%3E%3C/svg%3E",
        )


class MysteryViewTests(TestCase):
    def setUp(self):
        self.director1 = Director.objects.create(
            name="Rian Johnson", slug="rian-johnson"
        )
        self.movie1 = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            media_type=MysteryTitle.MediaType.MOVIE,
            description="Whodunit description",
            director=self.director1,
        )

        self.director2 = Director.objects.create(
            name="Steven Moffat", slug="steven-moffat"
        )
        self.movie2 = MysteryTitle.objects.create(
            title="Sherlock",
            slug="sherlock-2010",
            release_year=2010,
            media_type=MysteryTitle.MediaType.TV_SHOW,
            director=self.director2,
        )

    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "movies/movie_list.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_content(self):
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

    def test_detail_page_status_code(self):
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_page_template(self):
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/mystery_detail.html")

    def test_detail_page_content(self):
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Knives Out")
        self.assertContains(response, "2019")
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Whodunit description")
        self.assertContains(response, "Movie")

    def test_detail_page_404(self):
        url = reverse("movies:detail", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_detail_page_reviews_context(self):
        """Test that recent reviews are included in the detail page context."""
        user = get_user_model().objects.create_user(
            username="reviewer", password=secrets.token_urlsafe(16)
        )
        Review.objects.create(
            movie=self.movie1, user=user, quality=5, difficulty=3, is_fair_play=True
        )
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertIn("recent_reviews", response.context)
        self.assertEqual(len(response.context["recent_reviews"]), 1)
        self.assertEqual(response.context["total_reviews_count"], 1)

    def test_home_page_empty_list(self):
        MysteryTitle.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["movies"]), [])

    def test_pagination(self):
        """Test that the movie list is paginated."""
        # Create enough movies to trigger pagination
        for i in range(25):
            MysteryTitle.objects.create(
                title=f"Pagination Movie {i}",
                slug=f"pagination-movie-{i}",
                release_year=2020,
            )

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(
            len(response.context["movies"]), response.context["paginator"].per_page
        )
        self.assertGreater(response.context["paginator"].num_pages, 1)


class DirectorViewTests(TestCase):
    def setUp(self):
        self.director1 = Director.objects.create(
            name="Rian Johnson", slug="rian-johnson"
        )
        self.director2 = Director.objects.create(
            name="Alfred Hitchcock", slug="alfred-hitchcock"
        )

    def test_director_list_page_status_code(self):
        response = self.client.get(reverse("movies:director_list"))
        self.assertEqual(response.status_code, 200)

    def test_director_list_page_template(self):
        response = self.client.get(reverse("movies:director_list"))
        self.assertTemplateUsed(response, "movies/director_list.html")

    def test_director_list_page_context(self):
        response = self.client.get(reverse("movies:director_list"))
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Alfred Hitchcock")
        self.assertIn(self.director1, response.context["directors"])
        self.assertIn(self.director2, response.context["directors"])

    def test_director_detail_page_status_code(self):
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_director_detail_page_template(self):
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/director_detail.html")

    def test_director_detail_page_content(self):
        _ = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out",
            release_year=2019,
            director=self.director1,
        )
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Knives Out")


class SeriesViewTests(TestCase):
    def setUp(self):
        self.series1 = Series.objects.create(name="Benoit Blanc", slug="benoit-blanc")
        self.series2 = Series.objects.create(
            name="Sherlock Holmes", slug="sherlock-holmes"
        )

    def test_series_list_page_status_code(self):
        response = self.client.get(reverse("movies:series_list"))
        self.assertEqual(response.status_code, 200)

    def test_series_list_page_template(self):
        response = self.client.get(reverse("movies:series_list"))
        self.assertTemplateUsed(response, "movies/series_list.html")

    def test_series_list_page_context(self):
        response = self.client.get(reverse("movies:series_list"))
        self.assertContains(response, "Benoit Blanc")
        self.assertContains(response, "Sherlock Holmes")
        self.assertIn(self.series1, response.context["series_list"])
        self.assertIn(self.series2, response.context["series_list"])

    def test_series_detail_page_status_code(self):
        url = reverse("movies:series_detail", kwargs={"slug": self.series1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_series_detail_page_template(self):
        url = reverse("movies:series_detail", kwargs={"slug": self.series1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/series_detail.html")

    def test_series_detail_page_content(self):
        movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out",
            release_year=2019,
            series=self.series1,
        )
        url = reverse("movies:series_detail", kwargs={"slug": self.series1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Benoit Blanc")
        self.assertContains(response, "Knives Out")
        self.assertEqual(response.context["series"], self.series1)
        self.assertIn(movie, response.context["series"].movies.all())


class ReviewTests(TestCase):
    def setUp(self):
        self.uname = f"user_{secrets.token_hex(4)}"
        self.upass = secrets.token_urlsafe(16)

        self.user = get_user_model().objects.create_user(
            username=self.uname, password=self.upass
        )
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            media_type=MysteryTitle.MediaType.MOVIE,
        )
        self.url = reverse("movies:add_review", kwargs={"slug": self.movie.slug})

    def test_review_model_creation(self):
        review = Review.objects.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=3,
            is_fair_play=True,
            comment="Great movie!",
        )
        self.assertEqual(str(review), f"{self.user}'s review of {self.movie}")
        self.assertEqual(Review.objects.count(), 1)

    def test_unique_review_constraint(self):
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

    def test_create_view_login_required(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_create_view_get(self):
        self.client.login(username=self.uname, password=self.upass)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/review_form.html")
        self.assertEqual(response.context["movie"], self.movie)

    def test_create_view_post_success(self):
        self.client.login(username=self.uname, password=self.upass)
        data = {
            "quality": 5,
            "difficulty": 4,
            "is_fair_play": True,
            "comment": "Loved it",
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.movie.get_absolute_url())
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.quality, 5)
        self.assertEqual(review.user, self.user)

    def test_create_view_post_duplicate(self):
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
        self.assertEqual(Review.objects.first().quality, 3)

    def test_detail_view_context_has_reviewed(self):
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


class ReviewListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username=f"user_{secrets.token_hex(4)}", password=secrets.token_urlsafe(16)
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

    def test_review_list_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_review_list_context(self):
        response = self.client.get(self.url)
        self.assertIn(self.review, response.context["reviews"])
        self.assertEqual(response.context["movie"], self.movie)


class MysteryTitleStatsTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username=f"user_{secrets.token_hex(4)}", password=secrets.token_urlsafe(16)
        )
        self.user2 = get_user_model().objects.create_user(
            username=f"user_{secrets.token_hex(4)}", password=secrets.token_urlsafe(16)
        )

        self.movie = MysteryTitle.objects.create(
            title="Stats Movie",
            slug="stats-movie",
            release_year=2020,
        )

    def test_stats_calculation_and_signals(self):
        """Test that stats are updated when reviews are created, updated, or deleted."""
        # Initial state
        self.assertEqual(self.movie.avg_quality, 0.0)
        self.assertEqual(self.movie.avg_difficulty, 0.0)
        self.assertEqual(self.movie.fair_play_consensus, 0.0)

        # Add first review
        Review.objects.create(
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
        review2 = Review.objects.create(
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


class StaticFilesTests(TestCase):
    def test_heatmap_css_exists(self):
        """Test that the heatmap.css file is found by staticfiles finders."""
        # Verify the file exists in the expected namespaced location
        found_path = finders.find("movies/css/heatmap.css")
        self.assertIsNotNone(found_path)


class MovieStyleSheetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie = MysteryTitle.objects.create(
            title="Test Movie",
            release_year=2023,
            description="Test Description",
            slug="test-movie-2023",
        )

    def test_detail_view_loads_css(self):
        """Test that the mystery detail page loads the heatmap CSS."""
        response = self.client.get(self.movie.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/movies/css/heatmap')

    def test_review_list_view_loads_css(self):
        """Test that the review list page loads the heatmap CSS."""
        url = reverse("movies:review_list", args=[self.movie.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/movies/css/heatmap')
