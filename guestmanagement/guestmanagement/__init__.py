# Celery app is in the parent directory
try:
    from ..celery import app as celery_app
except ImportError:
    # Fallback for when the module is accessed differently
    pass

__all__ = ('celery_app',)