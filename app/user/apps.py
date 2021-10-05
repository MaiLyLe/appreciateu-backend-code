from django.apps import AppConfig


class UserConfig(AppConfig):
    """User app class"""
    name = 'user'

    def ready(self):
        """Overrides ready function to import signals"""
        #import user.signals  # noqa: F401
