![Rotting Research Logo](https://github.com/marshalmiller/rottingresearch/blob/a898614a4e933064a36478be259aee29b9f188fa/branding/project-banner/red/rottingresearch-github-project-banner-red.png)

# Introduction

This repository is for a Flask app that deliveries the [linkrot](https://github.com/rottingresearch/linkrot/) project.

# Mission

The mission of this project is to provide a place for researchers and scholars to check the links cited in their works and the works of others. The goal is to make publications more accessible and replicatable. This tool will coincide with research into persistent links and preserving the Internet and Commons at large.

# Installation

- Make sure that you have python and the latest version of pip installed.

  `python -m pip install --upgrade pip`

- Download Project

  `git clone https://github.com/rottingresearch/rottingresearch`

- Navigate to the root folder.

- Install Requirements

  `pip install -r requirements.txt`

- If using Windows, open app.py and set app.config['UPLOAD_FOLDER'] to a valid temporary folder.
- Set APP_SECRET_KEY environment variable before running the python script.

  Linux: `export APP_SECRET_KEY="random"`

  Windows: `setx APP_SECRET_KEY "random"`

- Run Flask App

  `python3 app.py`

- Run Celery worker

  `celery -A app:celery_app worker -B`

- Open 127.0.0.1:5000 on your browser.

# Docker Instructions

## Local Development

Docker-Compose is being used for local development mainly due to its ease of use and development.

- Set the `APP_SECRET_KEY`
- `docker-compose up --build -d` to run the container in detached mode.

The application is running on port `5000`. Docker volume is used so whenever changes are made they are reflected immediately. To view the container logs you can use `docker logs -f rottingresearch`. The `f` flag is used for following the logs.

## Building Image

- Clone repo `git clone https://github.com/rottingresearch/rottingresearch.git`
- Build the docker image `docker build --tag rottingresearch .`
- Run image `docker run -d -p 5000:5000 rottingresearch`

# Features

- Coming Soon

# Demo Site

The App is hosted at [https://rottingresearch.org/](https://rottingresearch.org/) during development.

# Code of Conduct

For our code of conduct please visit our [Code of Conduct page](https://github.com/rottingresearch/rottingresearch/blob/main/code_of_conduct.md).

# License

This program is licensed with an [MIT License](https://github.com/rottingresearch/linkrot/blob/main/LICENSE).
