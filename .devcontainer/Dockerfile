# Use the official uv image with Python 3.14
FROM ghcr.io/astral-sh/uv:python3.14-bookworm

# Install system dependencies
# - libpq-dev: for PostgreSQL (psycopg)
# - gettext: for Django translation commands
# - git: for version control in the container
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \gettext \
    curl \
    git \
    gnupg \
    libpq-dev \
    locales \
    vim \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Set the locale
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en

# Add alias to the system-wide bashrc so it's available for all users
COPY .devcontainer/bash_aliases.sh /tmp/bash_aliases.sh
RUN cat /tmp/bash_aliases.sh >> /etc/bash.bashrc && rm /tmp/bash_aliases.sh

# Set environment variables for uv
# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use the system Python environment for dependencies (simpler in containers)
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
# Ensure the path is correct
ENV PATH="/usr/local/bin:$PATH"

# Install Google Cloud CLI
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update && apt-get install -y google-cloud-cli \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workspace

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
