from .base import *
import environ
import os

env = environ.Env()

# IMPORTANT: Explicitly load .env from BASE_DIR (project root)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = False

# Secret Key (from .env or Render ENV)
SECRET_KEY = env("SECRET_KEY")

# Allow all hosts in Render
ALLOWED_HOSTS = ["*"]

# STATIC FILES
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# MEDIA FILES
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# WHITENOISE
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedStaticFilesStorage"

# DATABASE (Render Postgres OR .env SQLite)
DATABASES = {
    "default": env.db("DATABASE_URL")
}

try:
    from .local import *
except ImportError:
    pass
