import secrets
from typing import Any

from django.contrib.auth import get_user_model

from movies.models import MysteryTitle
from users.models import CustomUser


class UserFactory:
    @staticmethod
    def create(
        password: str | None = None,
        **kwargs: Any,
    ) -> tuple[CustomUser, str]:
        """Creates a user with a random username if not provided."""
        if "username" not in kwargs:
            kwargs["username"] = f"user_{secrets.token_hex(4)}"

        pwd = password or secrets.token_urlsafe(16)
        user = get_user_model().objects.create_user(password=pwd, **kwargs)
        return user, pwd


class MovieFactory:
    @staticmethod
    def create(**kwargs: Any) -> MysteryTitle:
        """Creates a MysteryTitle with sensible defaults."""
        defaults = {
            "title": f"Mystery {secrets.token_hex(2)}",
            "slug": f"mystery-{secrets.token_hex(4)}",
            "release_year": 2023,
            "media_type": MysteryTitle.MediaType.MOVIE,
        }
        defaults.update(kwargs)
        return MysteryTitle.objects.create(**defaults)
