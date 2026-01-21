# MysteryMovieClub

A web application for mystery enthusiasts to track, rate, and review mystery movies, TV shows, and miniseries. The platform focuses on rating titles not just by quality, but by the **difficulty** of the mystery and whether it adheres to **"Fair Play"** rules (solvable with the clues provided).

## 🕵️ Project Overview

Mystery Movie Club allows users to:
- **Discover Titles:** Browse a curated database of mystery movies, TV shows, and miniseries.
- **Track Directors & Series:** Follow works by specific directors (e.g., Rian Johnson) or within franchises (e.g., Benoit Blanc).
- **Rate & Review:** Submit detailed reviews including:
  - **Quality Score:** (1-5)
  - **Difficulty Score:** (1-5)
  - **Fair Play Assessment:** Was it solvable?
  - **Solved Status:** Did the user solve it before the reveal?
- **Tagging:** Categorize mysteries with community-driven tags.
- **Analyze:** View aggregate statistics on "Fair Play" consensus and difficulty.

## 🛠 Tech Stack

* **Language:** Python 3.14
* **Framework:** Django 6.0+
* **Package Manager:** [uv](https://github.com/astral-sh/uv)
* **Database:** SQLite (Default for Dev)
* **Styling:** Custom CSS / WhiteNoise for static files
* **Linting & Formatting:** Ruff
* **Type Checking:** Mypy (Strict)
* **Testing:** Pytest & pytest-django

## 🚀 Development Setup

### Option 1: GitHub Codespaces (Recommended)

This project is configured for **GitHub Codespaces**.
1.  Click the **Code** button on the repository page.
2.  Select **Codespaces** -> **Create codespace on main**.
3.  The container will automatically:
    * Install Python 3.14.
    * Install `uv`.
    * Sync all dependencies.
    * Run the `dev_setup.sh` script to set up the database, create a superuser, and seed initial data.

### Option 2: Local Development

#### Prerequisites
* Python 3.14+
* [uv](https://github.com/astral-sh/uv) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

#### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/mystery-movie-club.git](https://github.com/your-username/mystery-movie-club.git)
    cd mystery-movie-club
    ```

2.  **Run the Setup Script:**
    We provide a convenience script that handles dependency syncing, `.env` creation, migrations, and database seeding.
    ```bash
    bash dev_setup.sh
    ```

    *Alternatively, manual setup:*
    ```bash
    uv sync
    uv run pre-commit install --install-hooks
    # Create .env file with SECRET_KEY and DEBUG=True
    uv run python manage.py migrate
    uv run python manage.py createsuperuser
    ```

3.  **Run the Server:**
    ```bash
    uv run python manage.py runserver
    ```
    Access the site at `http://127.0.0.1:8000/`.

4.  **Access Admin:**
    * **URL:** `http://127.0.0.1:8000/admin/`
    * **Default Credentials** (created by `dev_setup.sh`):
        * Username: `admin`
        * Password: `admin`

5. **Persisting Gemini Login**
    ```bash
    # Log in to the gcloud tool
    gcloud auth login

    # Set up Application Default Credentials (used by Gemini Code Assist)
    gcloud auth application-default login
    ```

## 🧪 Testing

We use `pytest` for unit testing. All new features must include unit tests with docstrings.

**Run all tests:**
```bash
uv run pytest
```

**Run specific test file:**

```bash
uv run pytest movies/tests.py
```

## 🧹 Code Quality

This project enforces strict code quality standards.

* **Type Hinting:** All code must be fully typed and pass `mypy --strict`.
* **Formatting/Linting:** We use `ruff` for both linting and formatting.
* **Docstrings:** Required for all modules, classes, and functions (including tests).

**Run Type Checks:**

```bash
uv run mypy .
```

**Run Linter & Formatter:**

```bash
uv run ruff check .
uv run ruff format .
```

**Pre-commit Hooks:**
Hooks are installed automatically via `dev_setup.sh`. They run `ruff`, `mypy`, and other checks before every commit to ensure repository health.

## 📂 Project Structure

```text
├── .devcontainer/      # Codespaces configuration
├── config/             # Project-wide Django settings (settings, urls, wsgi)
├── movies/             # Core application (Models: MysteryTitle, Review, Director, etc.)
├── scripts/            # Management scripts (seeding data)
├── users/              # Custom user model application
├── manage.py           # Django management script
├── pyproject.toml      # Project configuration and dependencies (uv)
└── uv.lock             # Locked dependency versions

```

## 📝 Guidelines for Contributors

1. **Modular Design:** Keep apps decoupled. Use `movies` for content and `users` for authentication.
2. **Secrets:** Use `secrets` module instead of `random` for any security-related generation.
3. **Logging:** Import `logging` in every file and log significant events (e.g., `logger.info("Movie created: %s", title)`).
4. **Strict Typing:** Do not use `Any` unless absolutely necessary.

## 📄 License

See the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
