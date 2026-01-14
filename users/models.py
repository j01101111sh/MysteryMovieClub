import logging

from django.contrib.auth.models import AbstractUser

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    # Add any additional fields here if needed
    pass
