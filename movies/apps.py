from django.apps import AppConfig


class MoviesConfig(AppConfig):
    name = "movies"

    def ready(self) -> None:
        """
        Import signals when the app is ready.
        """
        import movies.signals  # noqa: F401
