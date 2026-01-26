from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from config.tests.factories import MovieFactory
from movies.models import MysteryTitle


class BaseTemplateTests(TestCase):
    def test_favicon_present(self) -> None:
        """Test that the favicon link tag is present in the base template."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<link rel="icon"')
        self.assertContains(
            response,
            "data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ctext y=%22.9em%22 font-size=%2290%22%3E🕵️%3C/text%3E%3C/svg%3E",
        )


class StaticFilesTests(TestCase):
    def test_heatmap_css_exists(self) -> None:
        """Test that the heatmap.css file is found by staticfiles finders."""
        # Verify the file exists in the expected namespaced location
        found_path = finders.find("movies/css/heatmap.css")
        self.assertIsNotNone(found_path)


class MovieStyleSheetTests(TestCase):
    movie: MysteryTitle

    @classmethod
    def setUpTestData(cls) -> None:
        cls.movie = MovieFactory.create()

    def test_detail_view_loads_css(self) -> None:
        """Test that the mystery detail page loads the heatmap CSS."""
        response = self.client.get(self.movie.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/movies/css/heatmap')

    def test_review_list_view_loads_css(self) -> None:
        """Test that the review list page loads the heatmap CSS."""
        url = reverse("movies:review_list", args=[self.movie.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/movies/css/heatmap')
