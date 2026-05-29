from library_service_api.settings.base import *

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

