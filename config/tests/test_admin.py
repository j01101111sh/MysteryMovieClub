from django.test import TestCase
from django.urls import reverse


class AdminAccessTests(TestCase):
    def test_admin_login_page_reachable(self) -> None:
        """
        Test that the admin login page is reachable via its reversed URL name.
        This ensures the test passes even if the admin URL path is changed.
        """
        url = reverse("admin:login")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Log in", response.content)
