from django.test import TestCase
from django.urls import reverse

from config.tests.factories import MovieFactory, UserFactory
from movies.models import WatchListEntry


class WatchListTests(TestCase):
    def setUp(self) -> None:
        self.user, self.upass = UserFactory.create()
        self.uname = self.user.get_username()
        self.movie = MovieFactory.create()

    def test_add_to_watchlist(self) -> None:
        self.client.login(username=self.uname, password=self.upass)
        url = reverse("movies:watchlist_toggle", kwargs={"slug": self.movie.slug})
        response = self.client.post(url)
        self.assertRedirects(response, self.movie.get_absolute_url())
        self.assertTrue(
            WatchListEntry.objects.filter(user=self.user, movie=self.movie).exists(),
        )

    def test_remove_from_watchlist(self) -> None:
        WatchListEntry.objects.create(user=self.user, movie=self.movie)
        self.client.login(username=self.uname, password=self.upass)
        url = reverse("movies:watchlist_toggle", kwargs={"slug": self.movie.slug})
        response = self.client.post(url)
        self.assertFalse(
            WatchListEntry.objects.filter(user=self.user, movie=self.movie).exists(),
        )
        self.assertRedirects(response, self.movie.get_absolute_url())

    def test_watchlist_view(self) -> None:
        WatchListEntry.objects.create(user=self.user, movie=self.movie)
        self.client.login(username=self.uname, password=self.upass)
        url = reverse("movies:watchlist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.title)


class WatchlistSignalTests(TestCase):
    """
    Unit tests for checking logging signals related to WatchListEntry.
    """

    def setUp(self) -> None:
        self.user, self.upass = UserFactory.create()
        self.uname = self.user.get_username()
        self.movie = MovieFactory.create()

    def test_watchlist_entry_creation_logging(self) -> None:
        """
        Test that creating a WatchListEntry triggers an INFO log message.
        """
        # We expect logs from the 'movies.signals' logger
        with self.assertLogs("movies.signals", level="INFO") as cm:
            WatchListEntry.objects.create(user=self.user, movie=self.movie)

            # Check that at least one log record matches our expectation
            expected_msg = f"Watchlist entry created: {self.user} added {self.movie.slug} to watchlist"
            self.assertTrue(
                any(expected_msg in record.getMessage() for record in cm.records),
                f"Expected log message '{expected_msg}' not found in {cm.output}",
            )

    def test_watchlist_entry_deletion_logging(self) -> None:
        """
        Test that deleting a WatchListEntry triggers an INFO log message.
        """
        # Create the entry first (this will also log, but we are not testing that here)
        entry = WatchListEntry.objects.create(user=self.user, movie=self.movie)

        # Now delete and check for the deletion log
        with self.assertLogs("movies.signals", level="INFO") as cm:
            entry.delete()

            expected_msg = f"Watchlist entry removed: {self.user} removed {self.movie.slug} from watchlist"
            self.assertTrue(
                any(expected_msg in record.getMessage() for record in cm.records),
                f"Expected log message '{expected_msg}' not found in {cm.output}",
            )
