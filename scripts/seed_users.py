import logging
import secrets
from typing import Any

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def create_users() -> None:
    """
    Seeds the database with sample users.
    """
    User = get_user_model()

    logger.info("Seeding users...")

    # 1. Define Sample Users
    # We generate 10 random users.
    num_users = 10
    user_data: list[dict[str, str]] = [
        {
            "username": (uname := f"user_{secrets.token_hex(8)}"),
            "email": f"{uname}@example.com",
            "password": secrets.token_urlsafe(16),
        }
        for _ in range(num_users)
    ]

    user_objects: list[Any] = []
    created_count = 0

    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "is_test_user": True,
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
            logger.info("Created user: %s", user.username)
            created_count += 1
        else:
            logger.info("User already exists: %s", user.username)
        user_objects.append(user)

    logger.info("Done! Created %s new users.", created_count)
