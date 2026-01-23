"""
URL configuration for config project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from config import views as config_views
from movies.views import MysteryListView

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", include("users.urls")),
    path(settings.ADMIN_URL or "admin/", admin.site.urls),
    path("movies/", include("movies.urls")),
    path("", MysteryListView.as_view(), name="home"),
]

handler404 = config_views.custom_page_not_found
handler403 = config_views.custom_permission_denied
handler400 = config_views.custom_bad_request
handler500 = config_views.custom_server_error
