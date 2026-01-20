import argparse
import logging
import os
import sys
from pathlib import Path

import django


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log output based on level and message content.
    """

    # ANSI Escape Codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    def format(self, record: logging.LogRecord) -> str:
        # Default color based on level
        color = self.WHITE
        if record.levelno >= logging.ERROR:
            color = self.RED
        elif record.levelno >= logging.WARNING:
            color = self.YELLOW
        elif record.levelno == logging.INFO:
            # Semantic coloring for seed script specific messages
            msg_str = str(record.msg)
            if ">>>" in msg_str:
                color = self.MAGENTA + self.BOLD
            elif "Created" in msg_str:
                color = self.GREEN
            elif "Updated" in msg_str:
                color = self.BLUE
            elif "Seeding" in msg_str:
                color = self.CYAN
            else:
                color = self.RESET

        # Format the timestamp and level
        # We manually format to inject color into the message part or the whole line
        # Here we color the whole line for simplicity and readability
        formatted_message = super().format(record)
        return f"{color}{formatted_message}{self.RESET}"


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
    # We define the format string
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers (e.g. from Django setup) to avoid duplicates
    root_logger.handlers = []

    if args.log_file:
        # File output: No colors
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)
    else:
        # Console output: Use ColoredFormatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredFormatter(log_format))
        root_logger.addHandler(console_handler)

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
