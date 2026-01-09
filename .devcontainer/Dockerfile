# Use the official uv image with Python 3.14
FROM ghcr.io/astral-sh/uv:python3.14-bookworm

# Install system dependencies
# - libpq-dev: for PostgreSQL (psycopg)
# - gettext: for Django translation commands
# - git: for version control in the container
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gettext \
    git \
    && rm -rf /var/lib/apt/lists/*

# Add alias to the system-wide bashrc so it's available for all users
RUN grep -qF "alias dj='uv run python manage.py'" /etc/bash.bashrc || echo "alias dj='uv run python manage.py'" >> /etc/bash.bashrc

# Set environment variables for uv
# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use the system Python environment for dependencies (simpler in containers)
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
# Ensure the path is correct
ENV PATH="/usr/local/bin:$PATH"

# Set the working directory
WORKDIR /workspace

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
