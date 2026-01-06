#!/bin/bash
set -e

echo "Starting development environment setup..."

# 1. Install uv if it's not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Ensure uv is in the PATH for the rest of this script execution
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "uv is already installed."
fi

# 2. Install dependencies through uv
# This creates the virtual environment and installs packages from uv.lock/pyproject.toml
echo "Syncing dependencies with uv..."
uv sync

# 3. Install pre-commit hooks
# We use 'uv run' to execute pre-commit from the project's virtual environment
if uv run pre-commit --version &> /dev/null; then
    echo "Installing pre-commit hooks..."
    uv run pre-commit install
else
    echo "Warning: 'pre-commit' not found in dependencies. Skipping hook installation."
    echo "Tip: Add it with 'uv add --dev pre-commit'"
fi

echo "Setup complete! You can now run 'uv run python manage.py runserver' or activate the environment."
