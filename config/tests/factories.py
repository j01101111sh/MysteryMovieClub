import secrets
from typing import Any

from django.contrib.auth import get_user_model
from django.utils.text import slugify

from movies.models import Collection, Director, MysteryTitle, Review, Series, Tag
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
        director = kwargs.pop("director", None) or DirectorFactory.create()
        series = kwargs.pop("series", None) or SeriesFactory.create()
        # Update defaults with any provided kwargs
        defaults.update(kwargs)

        movie = MysteryTitle.objects.create(**defaults)
        movie.director = director
        movie.series = series
        movie.save()
        return movie


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
            **kwargs: Fields to override (quality, difficulty, fair_play, etc.).

        Returns:
            A saved Review instance.
        """
        defaults = {
            "quality": 4,
            "difficulty": 3,
            "is_fair_play": True,
            "comment": "This is a test review content.",
        }

        defaults.update(kwargs)

        return Review.objects.create(user=user, movie=movie, **defaults)


class DirectorFactory:
    """
    Factory for creating Director instances.
    """

    @staticmethod
    def create(**kwargs: Any) -> Director:
        """
        Creates a new Director instance.

        Args:
            **kwargs: Fields to override.

        Returns:
            A saved Director instance.
        """
        name = kwargs.get("name", f"Director {secrets.token_hex(2)}")
        defaults = {
            "name": name,
            "slug": kwargs.get("slug", slugify(name) + f"-{secrets.token_hex(2)}"),
        }
        defaults.update(kwargs)

        return Director.objects.create(**defaults)


class SeriesFactory:
    """
    Factory for creating Series instances.
    """

    @staticmethod
    def create(**kwargs: Any) -> Series:
        """
        Creates a new Series instance.

        Args:
            **kwargs: Fields to override.

        Returns:
            A saved Series instance.
        """
        name = kwargs.get("name", f"Series {secrets.token_hex(2)}")
        defaults = {
            "name": name,
            "slug": kwargs.get("slug", slugify(name) + f"-{secrets.token_hex(2)}"),
        }
        defaults.update(kwargs)

        return Series.objects.create(**defaults)


class TagFactory:
    """
    Factory for creating Tag instances.
    """

    @staticmethod
    def create(**kwargs: Any) -> Tag:
        """
        Creates a new Tag instance.

        Args:
            **kwargs: Fields to override.

        Returns:
            A saved Tag instance.
        """
        name = kwargs.get("name", f"Tag-{secrets.token_hex(2)}")
        defaults = {
            "name": name,
            "slug": kwargs.get("slug", slugify(name) + f"-{secrets.token_hex(2)}"),
        }
        defaults.update(kwargs)

        return Tag.objects.create(**defaults)


class CollectionFactory:
    """
    Factory for creating Collection instances (user-created lists).
    """

    @staticmethod
    def create(user: CustomUser | None = None, **kwargs: Any) -> Collection:
        """
        Creates a new Collection instance.

        Args:
            user: The user creating the collection.
            **kwargs: Fields to override.

        Returns:
            A saved Collection instance.
        """
        if user is None:
            user, _ = UserFactory.create()

        name = kwargs.get("name", f"Collection {secrets.token_hex(2)}")
        defaults = {
            "name": name,
            "description": "A default collection description.",
            "is_public": True,
        }
        defaults.update(kwargs)

        return Collection.objects.create(user=user, **defaults)
