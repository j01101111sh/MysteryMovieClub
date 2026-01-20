#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
SU_NAME="admin"
SU_EMAIL="admin@example.com"
SU_PASSWORD="admin"

DEV_NAME="dev"
DEV_EMAIL="dev@dev.com"
DEV_PASSWORD="dev"

# 0. Delete existing dev files
if [ -f "db.sqlite3" ]; then
    echo "Deleting existing dev files..."
    rm "db.sqlite3" "django.log"
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
    echo "ADMIN_URL=admin/" >> .env
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

# 5b. Create Dev User (Idempotent)
echo "Checking for dev user..."
uv run python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='$DEV_NAME').exists():
    User.objects.create_user('$DEV_NAME', '$DEV_EMAIL', '$DEV_PASSWORD');
    print('Dev user created successfully.');
else:
    print('Dev user already exists. Skipping creation.');
"

# 6. Seed database
echo "Seeding database..."
uv run python scripts/seed_db.py --all

# 7. Verify Setup
echo "Verifying setup..."
uv run python manage.py check

echo "Setup complete."
echo "Run the server with: uv run python manage.py runserver"
