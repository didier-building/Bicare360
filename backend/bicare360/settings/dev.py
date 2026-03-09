"""
Development settings for bicare360 project.
"""
from .base import *

DEBUG = True

# Redis Cache Configuration (required for django-ratelimit)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

# Redis channel layer for development (production-like WebSocket handling)
# Use Redis for scalable real-time messaging
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# Fallback to in-memory if Redis is not available (uncomment if needed)
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer",
#     },
# }

# Development-specific apps (commented out if not installed)
INSTALLED_APPS += [
    # "django_extensions",
    # "debug_toolbar",
]

MIDDLEWARE += [
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Debug Toolbar
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Email backend for development
# Commented out to use .env EMAIL_BACKEND setting for real Gmail testing
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
