import secrets

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CustomUserCreationForm


class CustomUserModelTests(TestCase):
    def test_create_user(self) -> None:
        """Test that a user can be created with a username and password."""
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser", password=secrets.token_urlsafe(16)
        )
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self) -> None:
        """Test that a superuser can be created."""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="adminuser", password=secrets.token_urlsafe(16), email=None
        )
        self.assertEqual(admin_user.username, "adminuser")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_string_representation(self) -> None:
        """Test the model's string representation uses the username."""
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser2", password=secrets.token_urlsafe(16)
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
