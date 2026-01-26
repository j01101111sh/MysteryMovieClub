import secrets
from typing import Any

from django.contrib.auth import get_user_model
from django.utils.text import slugify

from movies.models import MysteryTitle, Review
from users.models import CustomUser

# Type alias for the user model
User = get_user_model()


class UserFactory:
    """
    Factory for creating Django User instances for testing purposes.
    """

    @staticmethod
    def create(
        password: str | None = None,
        **kwargs: Any,
    ) -> tuple[CustomUser, str]:
        """
        Creates a new user instance.

        Args:
            password: The password to set. If None, a random URL-safe string is generated.
            **kwargs: Additional fields for the user (e.g., username, email).

        Returns:
            A tuple containing (user_instance, plain_text_password).
        """
        if "username" not in kwargs:
            kwargs["username"] = f"user_{secrets.token_hex(4)}"

        if "email" not in kwargs:
            kwargs["email"] = f"{kwargs['username']}@example.com"

        plain_password = password or secrets.token_urlsafe(16)
        user = User.objects.create_user(password=plain_password, **kwargs)  # type: ignore

        return user, plain_password


class MovieFactory:
    """
    Factory for creating MysteryTitle instances for testing purposes.
    """

    @staticmethod
    def create(**kwargs: Any) -> MysteryTitle:
        """
        Creates a new MysteryTitle instance.

        Args:
            **kwargs: Fields to override default values.

        Returns:
            A saved MysteryTitle instance.
        """
        title = kwargs.get("title", f"Mystery {secrets.token_hex(2)}")

        defaults = {
            "title": title,
            "slug": kwargs.get("slug", slugify(title) + f"-{secrets.token_hex(2)}"),
            "release_year": 2023,
            "media_type": MysteryTitle.MediaType.MOVIE,
            "description": "A default test description.",
        }

        # Update defaults with any provided kwargs
        defaults.update(kwargs)

        return MysteryTitle.objects.create(**defaults)


class ReviewFactory:
    """
    Factory for creating Review instances for testing purposes.
    """

    @staticmethod
    def create(user: CustomUser, movie: MysteryTitle, **kwargs: Any) -> Review:
        """
        Creates a new Review instance.

        Args:
            user: The user authoring the review.
            movie: The movie being reviewed.
            **kwargs: Fields to override (rating, difficulty, fair_play, etc.).

        Returns:
            A saved Review instance.
        """
        defaults = {
            "rating": 80,
            "difficulty": 50,
            "fair_play": True,
            "title": "Test Review Title",
            "text": "This is a test review content.",
        }

        defaults.update(kwargs)

        return Review.objects.create(user=user, movie=movie, **defaults)
