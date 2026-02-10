# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (if needed for pdf tools, e.g. libpq-dev for postgres if used later, or others)
# For specific PDF tools like pdf2docx or img2pdf, we might need some libs, but usually pure python or basic libs suffice.
# If you need specific system libs, add them here.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
# We need SECRET_KEY for this, so we pass a dummy one if not provided, 
# or we can do it at runtime if we prefer (but build time is better for images)
RUN python manage.py collectstatic --noinput --clear

# Expose port 8000
EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
