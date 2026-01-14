from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.test import RequestFactory, TestCase, override_settings

from config.views import (
    custom_bad_request,
    custom_permission_denied,
    custom_server_error,
)


@override_settings(DEBUG=False)
class ErrorPageTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_404_page_not_found(self) -> None:
        """
        Test that a non-existent URL returns 404, uses our custom template, and logs the event.
        """
        # Watch the 'config.views' logger
        with self.assertLogs("config.views", level="WARNING") as cm:
            response = self.client.get("/non-existent-mystery-url/")

            self.assertEqual(response.status_code, 404)
            self.assertTemplateUsed(response, "404.html")
            self.assertIn(b"Mystery Missing", response.content)
            # Verify logging
            self.assertTrue(any("404 Page Not Found" in o for o in cm.output))

    def test_403_permission_denied(self) -> None:
        """
        Test that the permission_denied view renders 403.html, has content, and logs the event.
        """
        request = self.factory.get("/restricted/")

        with self.assertLogs("config.views", level="WARNING") as cm:
            response = custom_permission_denied(
                request,
                exception=PermissionDenied("Forbidden"),
            )

            self.assertEqual(response.status_code, 403)
            self.assertIn(b"Restricted Area", response.content)
            self.assertIn(b"don't have the clearance", response.content)
            # Verify logging
            self.assertTrue(any("403 Permission Denied" in o for o in cm.output))

    def test_400_bad_request(self) -> None:
        """
        Test that the bad_request view renders 400.html, has content, and logs the event.
        """
        request = self.factory.get("/bad-request/")

        with self.assertLogs("config.views", level="WARNING") as cm:
            response = custom_bad_request(
                request,
                exception=SuspiciousOperation("Bad Request"),
            )

            self.assertEqual(response.status_code, 400)
            self.assertIn(b"Red Herring Detected", response.content)
            # Verify logging
            self.assertTrue(any("400 Bad Request" in o for o in cm.output))

    def test_500_server_error(self) -> None:
        """
        Test that the server_error view renders 500.html, has content, and logs the event.
        """
        request = self.factory.get("/server-error/")

        # Check for ERROR level logs for 500
        with self.assertLogs("config.views", level="ERROR") as cm:
            response = custom_server_error(request)

            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Internal Investigation Underway", response.content)
            self.assertIn(
                b"The detectives have secured the perimeter",
                response.content,
            )
            # Verify logging
            self.assertTrue(any("500 Server Error" in o for o in cm.output))
