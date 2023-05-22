![Rotting Research Logo](https://github.com/marshalmiller/rottingresearch/blob/a898614a4e933064a36478be259aee29b9f188fa/branding/project-banner/red/rottingresearch-github-project-banner-red.png)

# Introduction

A project devoted to helping academics and researchers provide robust citations and mitigate link rot.

# Mission

Link rot is an established phenomenon that affects everyone who uses the internet. Researchers looking at individual subjects have recently addressed the extent of link rot’s influence on scholarly publications. One recent study found that 36% of all links in research articles were broken. 37% of DOIs, once seen as a tool to prevent link rot, were broken (Miller, 2022).

Rotting Research allows academics and researchers to upload their work and check the reliability of their citations. It extracts all of the links from the document and then checks to see if the link is accessible to the public.

Check out our website at https://rottingresearch.org.

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

- Open 127.0.0.1:8080 on your browser.

# Docker Instructions

## Local Development

Docker-Compose is being used for local development mainly due to its ease of use and development.

- Set the `APP_SECRET_KEY`
- `docker-compose up --build -d` to run the container in detached mode.

The application is running on port `8080`. Docker volume is used so whenever changes are made they are reflected immediately. To view the container logs you can use `docker logs -f rottingresearch`. The `f` flag is used for following the logs.

## Building Image

- Clone repo `git clone https://github.com/rottingresearch/rottingresearch.git`
- Build the docker image `docker build --tag rottingresearch .`
- Run image `docker run -d -p 8080:8080 rottingresearch`

# Features

- Coming Soon

# Demo Site

The App is hosted at [https://rottingresearch.org/](https://rottingresearch.org/) during development.

# Code of Conduct

For our code of conduct please visit our [Code of Conduct page](https://github.com/rottingresearch/rottingresearch/blob/main/code_of_conduct.md).

# License

This program is licensed with an [MIT License](https://github.com/rottingresearch/linkrot/blob/main/LICENSE).
