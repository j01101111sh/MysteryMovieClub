from django.test import TestCase
from django.urls import reverse

from config.tests.factories import ReviewFactory, UserFactory
from movies.models import MysteryTitle


class UserProfileTests(TestCase):
    def setUp(self) -> None:
        self.user, self.upass = UserFactory.create(
            bio="My mystery bio",
            location="Omaha, NE",
            website="https://mysite.com",
        )
        self.uname = self.user.get_username()
        self.movie = MysteryTitle.objects.create(
            title="Test Mystery",
            slug="test-mystery",
            release_year=2023,
            description="A test mystery description.",
        )

    def test_profile_view_status_code(self) -> None:
        """Test that the profile page returns a 200 status code."""
        url = reverse("profile", kwargs={"username": self.uname})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_template(self) -> None:
        """Test that the correct template is used for the profile page."""
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "users/user_detail.html")

    def test_profile_displays_user_details(self) -> None:
        """Test that the profile page displays the user's information including new fields."""
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "Member since")
        self.assertContains(response, "My mystery bio")
        self.assertContains(response, "Omaha, NE")
        self.assertContains(response, "https://mysite.com")

    def test_profile_displays_reviews(self) -> None:
        """Test that the profile page displays the user's reviews."""
        _ = ReviewFactory.create(
            movie=self.movie,
            user=self.user,
            quality=5,
            difficulty=4,
            is_fair_play=True,
            comment="This is a test review comment.",
        )

        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)

        self.assertContains(response, self.movie.title)
        self.assertContains(response, "This is a test review comment")
        self.assertContains(response, "Fair Play")
        self.assertEqual(len(response.context["reviews"]), 1)

    def test_profile_does_not_display_others_reviews(self) -> None:
        """Test that the profile page only shows the specific user's reviews."""
        other_user, _ = UserFactory.create()
        ReviewFactory.create(
            movie=self.movie,
            user=other_user,
        )

        url = reverse("profile", kwargs={"username": self.uname})
        response = self.client.get(url)

        self.assertNotContains(response, "Other user review")
        self.assertEqual(len(response.context["reviews"]), 0)

    def test_profile_empty_state(self) -> None:
        """Test the profile page when the user has no reviews."""
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertContains(response, "No reviews yet.")
        self.assertEqual(len(response.context["reviews"]), 0)

    def test_profile_view_404_for_non_existent_user(self) -> None:
        """Test that accessing a non-existent user profile returns a 404."""
        url = reverse("profile", kwargs={"username": "nonexistentuser"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_navigation_profile_link_authenticated(self) -> None:
        """Test that the 'My Profile' link appears for logged-in users."""
        self.client.login(username=self.uname, password=self.upass)
        url = reverse("profile", kwargs={"username": self.uname})
        response = self.client.get(url)

        profile_url = reverse("profile", kwargs={"username": self.uname})
        self.assertContains(response, f'href="{profile_url}">My Profile</a>')

    def test_navigation_profile_link_anonymous(self) -> None:
        """Test that the 'My Profile' link does not appear for anonymous users."""
        url = reverse("signup")
        response = self.client.get(url)
        self.assertNotContains(response, "My Profile")
