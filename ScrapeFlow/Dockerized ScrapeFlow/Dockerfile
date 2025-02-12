FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and dependencies for requests-html
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome options for headless execution
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver
ENV PYPPETEER_HOME=/app/.pyppeteer

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Set proper permissions
RUN chown -R nobody:nogroup /app
USER nobody

# Expose port
EXPOSE 8000

# Default command (override in docker-compose)
CMD ["gunicorn", "personal.wsgi:application", "--bind", "0.0.0.0:8000"]