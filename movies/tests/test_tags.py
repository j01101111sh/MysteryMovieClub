import secrets

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from movies.models import MysteryTitle, Tag, TagVote


class TagModelTests(TestCase):
    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="Whodunnit", slug="whodunnit")

    def test_string_representation(self) -> None:
        """Test that the tag's string representation is its name."""
        self.assertEqual(str(self.tag), "Whodunnit")

    def test_name_uniqueness(self) -> None:
        """Test that duplicate tag names raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Whodunnit", slug="other")

    def test_slug_uniqueness(self) -> None:
        """Test that duplicate tag slugs raise an IntegrityError."""
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Other", slug="whodunnit")


class TagVoteTests(TestCase):
    def setUp(self) -> None:
        self.upass = secrets.token_urlsafe(16)
        self.user = get_user_model().objects.create_user(  # type: ignore
            username="tagvoter",
            password=self.upass,
        )
        self.movie = MysteryTitle.objects.create(
            title="Tag Movie",
            slug="tag-movie",
            release_year=2021,
        )
        self.tag = Tag.objects.create(name="Suspense", slug="suspense")
        self.url = reverse("movies:vote_tag", kwargs={"slug": self.movie.slug})

    def test_tag_vote_logging(self) -> None:
        """Test that voting for a tag triggers a log message."""
        self.client.login(username="tagvoter", password=self.upass)

        # Test voting (adding)
        with self.assertLogs("movies.signals", level="INFO") as cm:
            self.client.post(self.url, {"tag_id": self.tag.id})
            self.assertTrue(
                any(
                    f"Tag vote created: {self.user} voted for {self.tag.slug} on {self.movie.slug}"
                    in o
                    for o in cm.output
                ),
            )

        # Test unvoting (removing)
        with self.assertLogs("movies.signals", level="INFO") as cm:
            self.client.post(self.url, {"tag_id": self.tag.id})
            self.assertTrue(
                any(
                    f"Tag vote removed: {self.user} voted for {self.tag.slug} on {self.movie.slug}"
                    in o
                    for o in cm.output
                ),
            )

    def test_uniqueness_constraint(self) -> None:
        """Test that a user cannot vote for the same tag on the same movie twice."""
        with self.assertRaises(IntegrityError):
            TagVote.objects.create(
                movie=self.movie,
                tag=self.tag,
                user=self.user,
            )
            TagVote.objects.create(
                movie=self.movie,
                tag=self.tag,
                user=self.user,
            )
