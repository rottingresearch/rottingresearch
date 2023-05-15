# Pull base image.
FROM python:3.11-slim

# Install Celery.
RUN pip install celery

# Define working directory.
WORKDIR /data

# Start Celery.
CMD celery -A app:celery_app worker -l info