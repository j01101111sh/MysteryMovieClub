import logging
import os
import sys
from pathlib import Path

import django
from django.utils.text import slugify

# Logger setup
logger = logging.getLogger(__name__)

# List of tags to create
SEED_TAGS: list[str] = [
    # Sub-genres
    "Whodunit",
    "Howcatchem",
    "Locked Room",
    "Cozy Mystery",
    "Noir",
    "Neo-Noir",
    "Police Procedural",
    "Hardboiled",
    "Giallo",
    "Historical Mystery",
    # Tropes & Plot Elements
    "Unreliable Narrator",
    "Plot Twist",
    "Red Herring",
    "Cold Case",
    "Serial Killer",
    "Amateur Sleuth",
    "Private Investigator",
    "Courtroom Drama",
    "Supernatural Elements",
    "Heist",
    # Tone & Style
    "Dark",
    "Humorous",
    "Campy",
    "Tense",
    "Slow Burn",
    "Fast-Paced",
    "Atmospheric",
    "Brain Burner",
]


def create_tags() -> None:
    """
    Populate the database with a standard set of mystery tags.
    """
    # Import models here to avoid AppRegistryNotReady errors if imported at module level before setup
    from movies.models import Tag

    logger.info("Checking %s tags...", len(SEED_TAGS))

    created_count = 0
    existing_count = 0

    for name in SEED_TAGS:
        slug = slugify(name)
        tag, created = Tag.objects.get_or_create(
            slug=slug,
            defaults={"name": name},
        )

        if created:
            created_count += 1
            logger.info("  [+] Created tag: %s", name)
        else:
            existing_count += 1
            # Optional: Update name formatting if it matches slug but differs in case
            if tag.name != name:
                tag.name = name
                tag.save()
                logger.info("  [~] Updated capitalization for: %s", name)

    logger.info("-" * 30)
    logger.info(
        "Finished tags! Created: %s | Existing: %s",
        created_count,
        existing_count,
    )


if __name__ == "__main__":
    # Setup Django environment for standalone execution
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(BASE_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    logging.basicConfig(level=logging.INFO)
    create_tags()
