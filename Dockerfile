# Use an official Python runtime based on Debian 12 "bookworm"
FROM python:3.12-slim-bookworm

# Add the wagtail user
RUN useradd wagtail

# Render dynamically assigns a PORT. Expose 10000 just for documentation.
EXPOSE 10000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=10000 \
    DJANGO_SETTINGS_MODULE=mysite.settings.production

# Install dependencies
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Install application server
RUN pip install "gunicorn==23.0.0" uvicorn

# Install project requirements
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Set working directory
WORKDIR /app

# Make sure wagtail owns this directory (needed for SQLite and static files)
RUN chown wagtail:wagtail /app

# Copy project files
COPY --chown=wagtail:wagtail . .

# Switch to wagtail user
USER wagtail

# Collect static
RUN python manage.py collectstatic --noinput --clear

# Automatically create a superuser if none exists
RUN python - <<'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", "Admin@123")
    print("Superuser created: admin / Admin@123")
else:
    print("Superuser already exists")
EOF

# Runtime command:
# 1. Migrate database
# 2. Start ASGI server using Gunicorn + Uvicorn worker
CMD set -xe; \
    python manage.py migrate --noinput; \
    gunicorn mysite.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
