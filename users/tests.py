import secrets

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from movies.models import MysteryTitle, Review
from users.forms import CustomUserCreationForm


class CustomUserModelTests(TestCase):
    def test_create_user(self) -> None:
        """Test that a user can be created with a username and password."""
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser",
            password=secrets.token_urlsafe(16),
        )
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self) -> None:
        """Test that a superuser can be created."""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="adminuser",
            password=secrets.token_urlsafe(16),
            email=None,
        )
        self.assertEqual(admin_user.username, "adminuser")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_string_representation(self) -> None:
        """Test the model's string representation uses the username."""
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser2",
            password=secrets.token_urlsafe(16),
        )
        self.assertEqual(str(user), "testuser2")


class SignUpViewTests(TestCase):
    def test_signup_page_status_code(self) -> None:
        """Test that the signup page returns a 200 status code."""
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_template(self) -> None:
        """Test that the correct template is used for the signup page."""
        response = self.client.get(reverse("signup"))
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_form(self) -> None:
        """Test that the signup form is the CustomUserCreationForm."""
        response = self.client.get(reverse("signup"))
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_signup(self) -> None:
        """Test that a user can be created by posting to the signup page."""
        User = get_user_model()
        self.assertEqual(User.objects.count(), 0)
        response = self.client.post(
            reverse("signup"),
            {"username": "newuser", "password": secrets.token_urlsafe(16)},
        )
        # Follow the redirect to the login page
        self.assertEqual(response.status_code, 200)

    def test_signup_csrf_error(self) -> None:
        """Test that the signup page enforces CSRF protection."""
        # Create a client that enforces CSRF checks
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(
            reverse("signup"),
            {"username": "csrf_test_user", "password": secrets.token_urlsafe(16)},
        )

        # Expect a 403 Forbidden response due to missing CSRF token
        self.assertEqual(response.status_code, 403)


class UserProfileTests(TestCase):
    def setUp(self) -> None:
        self.User = get_user_model()
        self.upass = secrets.token_urlsafe(16)
        self.user = self.User.objects.create_user(
            username="profileuser",
            password=self.upass,
        )
        self.movie = MysteryTitle.objects.create(
            title="Test Mystery",
            slug="test-mystery",
            release_year=2023,
            description="A test mystery description.",
        )

    def test_profile_view_status_code(self) -> None:
        """Test that the profile page returns a 200 status code."""
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_template(self) -> None:
        """Test that the correct template is used for the profile page."""
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertTemplateUsed(response, "users/user_detail.html")

    def test_profile_displays_user_details(self) -> None:
        """Test that the profile page displays the user's information."""
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "Member since")

    def test_profile_displays_reviews(self) -> None:
        """Test that the profile page displays the user's reviews."""
        Review.objects.create(
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
        other_user = self.User.objects.create_user(
            username="otheruser",
            password=secrets.token_urlsafe(16),
        )
        Review.objects.create(
            movie=self.movie,
            user=other_user,
            quality=1,
            difficulty=1,
            is_fair_play=False,
            comment="Other user review",
        )

        url = reverse("profile", kwargs={"username": self.user.username})
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
        self.client.login(username="profileuser", password=self.upass)
        url = reverse("profile", kwargs={"username": self.user.username})
        response = self.client.get(url)

        profile_url = reverse("profile", kwargs={"username": self.user.username})
        self.assertContains(response, f'href="{profile_url}">My Profile</a>')

    def test_navigation_profile_link_anonymous(self) -> None:
        """Test that the 'My Profile' link does not appear for anonymous users."""
        url = reverse("signup")
        response = self.client.get(url)
        self.assertNotContains(response, "My Profile")
