from .base import *  # noqa: F403
from .base import BASE_DIR, env

DEBUG = False
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'test_db.sqlite3'}"),
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
