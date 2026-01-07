from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from movies.models import Director, MysteryTitle


class MysteryTitleModelTests(TestCase):
    def setUp(self):
        self.director = Director.objects.create(
            name="Rian Johnson", slug="rian-johnson"
        )
        self.movie = MysteryTitle.objects.create(
            title="Knives Out",
            slug="knives-out-2019",
            release_year=2019,
            description="A detective investigates...",
            media_type=MysteryTitle.MediaType.MOVIE,
        )
        self.movie.directors.add(self.director)

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
        )
        self.movie1.directors.add(self.director1)

        self.director2 = Director.objects.create(
            name="Steven Moffat", slug="steven-moffat"
        )
        self.movie2 = MysteryTitle.objects.create(
            title="Sherlock",
            slug="sherlock-2010",
            release_year=2010,
            media_type=MysteryTitle.MediaType.TV_SHOW,
        )
        self.movie2.directors.add(self.director2)

    def test_home_page_status_code(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_home_page_content(self):
        """Test that the list view context contains our movies and directors."""
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

    def test_home_page_empty_list(self):
        MysteryTitle.objects.all().delete()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["movies"]), [])


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
        movie = MysteryTitle.objects.create(
            title="Knives Out", slug="knives-out", release_year=2019
        )
        movie.directors.add(self.director1)
        url = reverse("movies:director_detail", kwargs={"slug": self.director1.slug})
        response = self.client.get(url)
        self.assertContains(response, "Rian Johnson")
        self.assertContains(response, "Knives Out")
