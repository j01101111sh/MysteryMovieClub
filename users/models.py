import logging
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models.base import ModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    # Add any additional fields here if needed
    pass


@receiver(post_save, sender=CustomUser)
def log_user_creation(
    sender: ModelBase,
    instance: CustomUser,
    created: bool,
    **kwargs: Any,
) -> None:
    """Log a message whenever a new user is created."""
    if created:
        logger.info("User created (signal): %s", instance.username)
