from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from movies.models import Director
from movies.tests.factories import MovieFactory


class DirectorModelTests(TestCase):
    def setUp(self) -> None:
        self.director = Director.objects.create(
            name="Alfred Hitchcock",
            slug="alfred-hitchcock",
        )

    def test_string_representation(self) -> None:
        """Test that the model's string representation returns the director's name."""
        self.assertEqual(str(self.director), "Alfred Hitchcock")

    def test_get_absolute_url(self) -> None:
        """Test that get_absolute_url generates the correct path for a director."""
        expected_url = reverse(
            "movies:director_detail",
            kwargs={"slug": self.director.slug},
        )
        self.assertEqual(self.director.get_absolute_url(), expected_url)

    def test_slug_uniqueness(self) -> None:
        """Test that duplicate slugs for directors raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Director.objects.create(name="Hitchcock", slug="alfred-hitchcock")

    def test_name_uniqueness(self) -> None:
        """Test that duplicate names for directors raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Director.objects.create(name="Alfred Hitchcock", slug="hitchcock")

    def test_director_creation_logging(self) -> None:
        """Test that creating a director triggers a log message."""
        with self.assertLogs("movies.signals", level="INFO") as cm:
            Director.objects.create(
                name="Log Test Director",
                slug="log-test-director",
            )

            # Verify the log message exists
            self.assertTrue(
                any("Director created: log-test-director" in o for o in cm.output),
            )


class DirectorViewTests(TestCase):
    def setUp(self) -> None:
        self.director1 = Director.objects.create(
            name="Rian Johnson",
            slug="rian-johnson",
        )
        self.director2 = Director.objects.create(
            name="Alfred Hitchcock",
            slug="alfred-hitchcock",
        )

    def test_director_list_page_status_code(self) -> None:
        """Test that the director list page returns a 200 OK status code."""
        response = self.client.get(reverse("movies:director_list"))
        self.assertEqual(response.status_code, 200)

    def test_director_list_page_template(self) -> None:
        """Test that the director list page uses the correct template."""
        response = self.client.get(reverse("movies:director_list"))
        self.assertTemplateUsed(response, "movies/director_list.html")

    def test_director_list_page_context(self) -> None:
        """Test that the director list page context contains the directors."""
        response = self.client.get(reverse("movies:director_list"))
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Alfred Hitchcock")
        self.assertIn(self.director1, response.context["directors"])
        self.assertIn(self.director2, response.context["directors"])

    def test_director_detail_page_status_code(self) -> None:
        """Test that a valid director detail page returns a 200 OK status code."""
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_director_detail_page_template(self) -> None:
        """Test that the director detail page uses the correct template."""
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "movies/director_detail.html")

    def test_director_detail_page_content(self) -> None:
        """Test that the director detail page displays the director's movies."""
        _ = MovieFactory.create(title="Knives Out", director=self.director1)
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Knives Out")

    def test_director_detail_page_context_plot_data(self) -> None:
        """Test that the director detail page context contains the plot data and averages."""
        # Create a movie with stats associated with director1
        _ = MovieFactory.create(
            title="Knives Out",
            director=self.director1,
            avg_quality=4.5,
            avg_difficulty=3.0,
        )

        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("plot_data", response.context)
        self.assertIn("avg_difficulty", response.context)
        self.assertIn("avg_quality", response.context)

        # plot_data should be a list
        plot_data = response.context["plot_data"]
        self.assertIsInstance(plot_data, list)
        self.assertEqual(len(plot_data), 1)
        self.assertEqual(plot_data[0]["title"], "Knives Out")
        self.assertEqual(plot_data[0]["x"], 3.0)
        self.assertEqual(plot_data[0]["y"], 4.5)

        # Check averages
        self.assertEqual(response.context["avg_difficulty"], 3.0)
        self.assertEqual(response.context["avg_quality"], 4.5)
