from .settings import *  # noqa: F401,F403

# Tests must use SQLite per the spec. Validate migrations with `manage.py migrate --check`.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
