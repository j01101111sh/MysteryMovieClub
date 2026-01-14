import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Get logger for this module
logger = logging.getLogger(__name__)


def custom_page_not_found(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    """Custom 404 handler that logs the error."""
    logger.warning("404 Page Not Found: %s", request.path)
    return render(request, "404.html", status=404)


def custom_permission_denied(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    """Custom 403 handler that logs the error."""
    logger.warning("403 Permission Denied: %s", request.path)
    return render(request, "403.html", status=403)


def custom_bad_request(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    """Custom 400 handler that logs the error."""
    logger.warning("400 Bad Request: %s", request.path)
    return render(request, "400.html", status=400)


def custom_server_error(request: HttpRequest) -> HttpResponse:
    """Custom 500 handler that logs the error."""
    logger.error("500 Server Error: %s", request.path)
    return render(request, "500.html", status=500)
