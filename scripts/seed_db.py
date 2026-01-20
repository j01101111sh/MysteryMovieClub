import argparse
import logging
import os
import sys
from pathlib import Path

import django


def setup_django() -> None:
    """
    Initialize the Django environment.
    """
    base_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(base_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()


def main() -> None:
    """
    Main controller script for seeding the database.
    """
    parser = argparse.ArgumentParser(description="Seed the database with initial data.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all seed scripts (Tags -> Movies -> Reviews)",
    )
    parser.add_argument("--tags", action="store_true", help="Seed tags")
    parser.add_argument("--movies", action="store_true", help="Seed movies")
    parser.add_argument("--reviews", action="store_true", help="Seed reviews/users")
    parser.add_argument(
        "--log-file",
        type=str,
        help="Optional file path to write logs to. If not provided, logs to console.",
    )

    args = parser.parse_args()

    # If no seed arguments provided, print help and exit early
    if not any([args.all, args.tags, args.movies, args.reviews]):
        parser.print_help()
        return

    # 1. Setup Django (Loads settings.py, which might have its own logging config)
    setup_django()

    # 2. Configure Logging
    # We use force=True to override any logging config applied by django.setup()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,
        filename=args.log_file if args.log_file else None,
    )
    logger = logging.getLogger(__name__)

    # 3. Import seed modules
    # Try/Except handles running this script from root (python -m scripts.seed_db)
    # vs running from inside scripts/ directory directly.
    from scripts import seed_movies, seed_reviews, seed_tags

    # 4. Execute Logic
    if args.all or args.tags:
        logger.info(">>> Starting Tag Seed")
        seed_tags.create_tags()

    if args.all or args.movies:
        logger.info(">>> Starting Movie Seed")
        seed_movies.create_movies()

    if args.all or args.reviews:
        logger.info(">>> Starting Review Seed")
        seed_reviews.create_reviews()

    logger.info(">>> Seeding Complete")


if __name__ == "__main__":
    main()
