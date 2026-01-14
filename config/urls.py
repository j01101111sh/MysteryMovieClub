"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from config import views as config_views
from movies.views import MysteryListView

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", include("users.urls")),
    path("admin/", admin.site.urls),
    path("movies/", include("movies.urls")),
    path("", MysteryListView.as_view(), name="home"),
]

handler404 = config_views.custom_page_not_found
handler403 = config_views.custom_permission_denied
handler400 = config_views.custom_bad_request
handler500 = config_views.custom_server_error
