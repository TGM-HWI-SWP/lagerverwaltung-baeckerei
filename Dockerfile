# Dockerfile for Flask Web-UI (Lagerverwaltung Bäckerei)
# Standard: Web App für Docker Compose (keine PyQt6)

FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV REPOSITORY_TYPE=mongodb

# Install minimal system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -e .

EXPOSE 5000

CMD ["python", "-m", "src.ui.flask_app"]