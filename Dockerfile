# Use an official Python runtime based on Debian 12 "bookworm"
FROM python:3.12-slim-bookworm

# Add wagtail user
RUN useradd wagtail

# Render will provide PORT dynamically (default 10000)
ENV PYTHONUNBUFFERED=1 \
    PORT=10000 \
    DJANGO_SETTINGS_MODULE=mysite.settings.production

# Install dependencies for Django/Wagtail
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Install server packages
RUN pip install "gunicorn==23.0.0" uvicorn

# Install project requirements
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Set working directory
WORKDIR /app

# Ensure wagtail user owns this folder
RUN chown wagtail:wagtail /app

# Copy project
COPY --chown=wagtail:wagtail . .

# Switch to wagtail user
USER wagtail

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# --------------------------
# ✔ SUPERUSER CREATION MOVED INTO CMD
# --------------------------

# Runtime command:
# 1. migrate
# 2. create superuser if missing
# 3. run server
CMD set -xe; \
    python manage.py migrate --noinput; \
    python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); \
        User.objects.filter(username='admin').exists() or \
        User.objects.create_superuser('admin','admin@example.com','Admin@123')"; \
    gunicorn mysite.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT}
