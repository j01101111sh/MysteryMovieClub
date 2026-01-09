#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -ex

# Configuration
SU_NAME="admin"
SU_EMAIL="admin@example.com"
SU_PASSWORD="admin"

# 0. Delete existing dev database
if [ -f "db.sqlite3" ]; then
    echo "Deleting existing dev database..."
    rm "db.sqlite3"
fi

# 1. Sync Dependencies (uv)
echo "Syncing dependencies with uv..."
uv sync

# 2. Install pre-commit hooks
echo "Installing pre-commit hooks..."
uv run pre-commit install --install-hooks

# 3. Check for .env file
if [ ! -f .env ]; then
    echo ".env file not found. Generating new file with Django SECRET_KEY..."
    echo "SECRET_KEY=$(uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > .env
    echo "Setting DEBUG to True for dev environments..."
    echo "DEBUG=True" >> .env
    echo "CSRF_TRUSTED_ORIGINS=https://localhost:8000,https://*.github.dev,https://*.app.github.dev" >> .env
    echo "Done: .env created."
else
    echo ".env file already exists. Skipping generation."
fi

# 4. Run Django migrations
echo "Running database migrations..."
uv run python manage.py migrate

# 5. Create Superuser (Idempotent)
echo "Checking for superuser..."
uv run python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='$SU_NAME').exists():
    User.objects.create_superuser('$SU_NAME', '$SU_EMAIL', '$SU_PASSWORD');
    print('Superuser created successfully.');
else:
    print('Superuser already exists. Skipping creation.');
"

# 6. Seed movie database
echo "Seeding movie database..."
uv run python scripts/seed_movies.py

# 7. Seed reviews
echo "Seeding reviews..."
uv run python scripts/seed_reviews.py

# 8. Verify Setup
echo "Verifying setup..."
uv run python manage.py check

echo "Setup complete."
echo "Run the server with: uv run python manage.py runserver"
