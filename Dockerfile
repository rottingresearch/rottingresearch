# Base Image
FROM python:3.11-slim

# Copying Files
COPY requirements.txt requirements.txt
# Installing packages
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python-dev 
RUN pip install -r requirements.txt

COPY . .

# Start Flask App
CMD python app.py

# Expose Port
EXPOSE 8080
