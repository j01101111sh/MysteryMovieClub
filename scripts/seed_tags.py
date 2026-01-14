import os
import sys
from pathlib import Path

import django
from django.utils.text import slugify

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from movies.models import Tag  # noqa: E402

# List of tags to create
seed_tags = [
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


def run() -> None:
    """Populate the database with a standard set of mystery tags."""

    print(f"Checking {len(seed_tags)} tags...")

    created_count = 0
    existing_count = 0

    for name in seed_tags:
        slug = slugify(name)
        tag, created = Tag.objects.get_or_create(
            slug=slug,
            defaults={"name": name},
        )

        if created:
            created_count += 1
            print(f"  [+] Created tag: {name}")
        else:
            existing_count += 1
            # Optional: Update name formatting if it matches slug but differs in case
            if tag.name != name:
                tag.name = name
                tag.save()
                print(f"  [~] Updated capitalization for: {name}")

    print("-" * 30)
    print(f"Finished! Created: {created_count} | Existing: {existing_count}")


if __name__ == "__main__":
    run()
