from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Import here to avoid AppRegistryNotReady issues
        from .logging import configure_logging
        configure_logging()