from django.urls import path

from users.views import SignUpView, UserDetailView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/<str:username>/", UserDetailView.as_view(), name="profile"),
]
