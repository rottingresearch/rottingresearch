FROM python:3.9

WORKDIR /app
COPY . .

# Installing packages
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python-dev 
RUN pip3 install -r requirements.txt
CMD [ "python3", "./app.py" ]