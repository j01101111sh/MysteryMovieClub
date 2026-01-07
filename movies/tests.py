from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from movies.models import MysteryTitle


class MysteryTitleModelTests(TestCase):
    def setUp(self):
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            director="Rian Johnson",
            description="A detective investigates...",
            media_type=MysteryTitle.MediaType.MOVIE,
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
        # self.movie is "Knives Out" (2019)
        m_older = MysteryTitle.objects.create(
            title="A Older", slug="older", release_year=2018
        )
        m_newer = MysteryTitle.objects.create(
            title="Z Newer", slug="newer", release_year=2020
        )
        m_same_year = MysteryTitle.objects.create(
            title="A Same Year", slug="same-year", release_year=2019
        )

        # Expected order: 2020, 2019 (A..), 2019 (Knives..), 2018
        expected = [m_newer, m_same_year, self.movie, m_older]
        self.assertEqual(list(MysteryTitle.objects.all()), expected)

    def test_slug_uniqueness(self):
        """Test that duplicate slugs raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            # Attempt to create a movie with the same slug as self.movie
            MysteryTitle.objects.create(
                title="Dup", slug=self.movie.slug, release_year=2020
            )


class BaseTemplateTests(TestCase):
    def test_favicon_present(self):
        """
        Test that the base template includes the correct favicon.
        """
        # Request the home page, which extends base.html
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # Check for the presence of the favicon link tag
        self.assertContains(response, '<link rel="icon"')

        # Check for the specific SVG data URI
        self.assertContains(
            response,
            "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🕵️</text></svg>",
        )


class MysteryViewTests(TestCase):
    def setUp(self):
        self.movie1 = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            director="Rian Johnson",
            media_type=MysteryTitle.MediaType.MOVIE,
            description="Whodunit description",
        )
        self.movie2 = MysteryTitle.objects.create(
            title="Sherlock",
            slug="sherlock-2010",
            release_year=2010,
            director="Steven Moffat",
            media_type=MysteryTitle.MediaType.TV_SHOW,
        )

    def test_home_page_status_code(self):
        """Test that the home page loads successfully."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        """Test that the home page uses the correct templates."""
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_context(self):
        """Test that the list view context contains our movies."""
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Knives Out")
        self.assertContains(response, "Sherlock")

        movies_in_context = response.context["movies"]
        self.assertIn(self.movie1, movies_in_context)
        self.assertIn(self.movie2, movies_in_context)

    def test_detail_page_status_code(self):
        """Test that a valid detail page loads successfully."""
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_page_template(self):
        """Test that the detail page uses the correct template."""
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/mystery_detail.html")

    def test_detail_page_content(self):
        """Test that the detail page displays specific movie information."""
        url = reverse("movies:detail", kwargs={"slug": self.movie1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Knives Out")
        self.assertContains(response, "2019")
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Whodunit description")
        # "Movie" is the display value for MediaType.MOVIE
        self.assertContains(response, "Movie")

    def test_detail_page_404(self):
        """Test that accessing a non-existent slug returns a 404."""
        url = reverse("movies:detail", kwargs={"slug": "non-existent-slug"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_home_page_empty_list(self):
        """Test that the home page loads correctly with no data."""
        MysteryTitle.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["movies"]), [])
