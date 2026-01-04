# Base Image
<<<<<<< HEAD
FROM python:3.14.2-slim
=======
FROM python:3.12-slim
>>>>>>> 853274c (WIP: investigate lxml build issues in worker)

COPY requirements.txt requirements.txt

# Installing packages
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python-dev-is-python3 \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt

# Copying files
COPY . .

# Start Flask App
# CMD ["python", "app.py"]
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
# Expose Port
EXPOSE 8000
