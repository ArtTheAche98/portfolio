FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies (including libraries for lxml)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev libxml2-dev libxslt1-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app

# Expose port (adjust if necessary)
EXPOSE 8000

# Default command runs the web server; override in Compose for Celery tasks
CMD ["gunicorn", "personal.wsgi:application", "--bind", "0.0.0.0:8000"]