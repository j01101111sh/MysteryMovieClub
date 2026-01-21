from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from movies.models import MysteryTitle, Series


class SeriesModelTests(TestCase):
    def setUp(self) -> None:
        self.series = Series.objects.create(name="Benoit Blanc", slug="benoit-blanc")

    def test_string_representation(self) -> None:
        """Test that the model's string representation returns the series name."""
        self.assertEqual(str(self.series), "Benoit Blanc")

    def test_get_absolute_url(self) -> None:
        """Test that get_absolute_url generates the correct path for a series."""
        expected_url = reverse(
            "movies:series_detail",
            kwargs={"slug": self.series.slug},
        )
        self.assertEqual(self.series.get_absolute_url(), expected_url)

    def test_slug_uniqueness(self) -> None:
        """Test that duplicate slugs for series raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Series.objects.create(name="Blanc", slug="benoit-blanc")

    def test_name_uniqueness(self) -> None:
        """Test that duplicate names for series raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Series.objects.create(name="Benoit Blanc", slug="blanc")

    def test_series_creation_logging(self) -> None:
        """Test that creating a series triggers a log message."""
        with self.assertLogs("movies.signals", level="INFO") as cm:
            Series.objects.create(
                name="Log Test Series",
                slug="log-test-series",
            )

            # Verify the log message exists
            self.assertTrue(
                any("Series created: log-test-series" in o for o in cm.output),
            )


class SeriesViewTests(TestCase):
    def setUp(self) -> None:
        self.series1 = Series.objects.create(name="Benoit Blanc", slug="benoit-blanc")
        self.series2 = Series.objects.create(
            name="Sherlock Holmes",
            slug="sherlock-holmes",
        )

    def test_series_list_page_status_code(self) -> None:
        """Test that the series list page returns a 200 OK status code."""
        response = self.client.get(reverse("movies:series_list"))
        self.assertEqual(response.status_code, 200)

    def test_series_list_page_template(self) -> None:
        """Test that the series list page uses the correct template."""
        response = self.client.get(reverse("movies:series_list"))
        self.assertTemplateUsed(response, "movies/series_list.html")

    def test_series_list_page_context(self) -> None:
        """Test that the series list page context contains the series."""
        response = self.client.get(reverse("movies:series_list"))
        self.assertContains(response, "Benoit Blanc")
        self.assertContains(response, "Sherlock Holmes")
        self.assertIn(self.series1, response.context["series_list"])
        self.assertIn(self.series2, response.context["series_list"])

    def test_series_detail_page_status_code(self) -> None:
        """Test that a valid series detail page returns a 200 OK status code."""
        url = reverse("movies:series_detail", kwargs={"slug": self.series1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_series_detail_page_template(self) -> None:
        """Test that the series detail page uses the correct template."""
        url = reverse("movies:series_detail", kwargs={"slug": self.series1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/series_detail.html")

    def test_series_detail_page_content(self) -> None:
        """Test that the series detail page displays the series' movies."""
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

    def test_series_detail_stats(self) -> None:
        """Test that the series detail page displays correct aggregate statistics."""
        # Create movies with specific stats
        MysteryTitle.objects.create(
            title="Glass Onion",
            slug="glass-onion",
            release_year=2022,
            series=self.series1,
            avg_quality=4.0,
            avg_difficulty=3.0,
        )
        MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out",
            release_year=2019,
            series=self.series1,
            avg_quality=5.0,
            avg_difficulty=4.0,
        )
        # Create a movie with no stats (should be ignored in average)
        MysteryTitle.objects.create(
            title="Wake Up Dead Man",
            slug="wake-up-dead-man",
            release_year=2025,
            series=self.series1,
            avg_quality=0.0,
            avg_difficulty=0.0,
        )

        url = reverse("movies:series_detail", kwargs={"slug": self.series1.slug})
        response = self.client.get(url)

        # Average Quality: (4.0 + 5.0) / 2 = 4.5
        # Average Difficulty: (3.0 + 4.0) / 2 = 3.5
        self.assertEqual(response.context["avg_quality"], 4.5)
        self.assertEqual(response.context["avg_difficulty"], 3.5)
        self.assertContains(response, "4.5")
        self.assertContains(response, "3.5")
