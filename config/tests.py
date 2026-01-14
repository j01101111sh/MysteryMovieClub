from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.test import RequestFactory, TestCase, override_settings
from django.views.defaults import bad_request, permission_denied, server_error


# We override DEBUG to False to ensure we are testing the production error handling
# logic rather than the debug tracebacks.
@override_settings(DEBUG=False)
class ErrorPageTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_404_page_not_found(self) -> None:
        """
        Test that a non-existent URL returns 404 and uses our custom template.
        """
        # For 404, we can simply use the client because the URL router handles it naturally
        response = self.client.get("/non-existent-mystery-url/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertIn(b"Mystery Missing", response.content)

    def test_403_permission_denied(self) -> None:
        """
        Test that the permission_denied view renders 403.html with our content.
        """
        request = self.factory.get("/")
        # specific exception is required by the view signature
        response = permission_denied(request, exception=PermissionDenied("Forbidden"))

        self.assertEqual(response.status_code, 403)
        # Note: We check content instead of assertTemplateUsed because invoking
        # views directly bypasses some template instrumentation.
        self.assertIn(b"Restricted Area", response.content)
        self.assertIn(b"don't have the clearance", response.content)

    def test_400_bad_request(self) -> None:
        """
        Test that the bad_request view renders 400.html with our content.
        """
        request = self.factory.get("/")
        response = bad_request(request, exception=SuspiciousOperation("Bad Request"))

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Red Herring Detected", response.content)

    def test_500_server_error(self) -> None:
        """
        Test that the server_error view renders 500.html with our content.
        """
        request = self.factory.get("/")
        response = server_error(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Internal Investigation Underway", response.content)
        self.assertIn(b"The detectives have secured the perimeter", response.content)
