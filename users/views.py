from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from .forms import CustomUserCreationForm

User = get_user_model()


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")  # Assuming 'login' URL will exist
    template_name = "registration/signup.html"


class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.review_set.select_related("movie").order_by(
            "-created_at"
        )
        return context
