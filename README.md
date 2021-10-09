# Introduction

This repository is for a Flask app that deliveries the [linkrot](https://github.com/marshalmiller/linkrot/) project.

# Mission

The mission of this project is to provide a place for researchers and scholars to check the links cited in their works and the works of others. The goal is to make publications more accessible and replicatable. This tool will coincide with research into persistent links and preserving the Internet and Commons at large.

# Installation

- Make sure that you have python and the latest version of pip installed.

  `python -m pip install --upgrade pip`

- Download Project

  `wget https://github.com/marshalmiller/rottingresearch`

- Navigate to the root folder.

- Install Requirements

  `pip install -r requirements.txt`

- If using Windows, open app.py and set app.config['UPLOAD_FOLDER'] to a valid temporary folder.
- Set APP_SECRET_KEY environment variable before running the python script.

  Linux: `export APP_SECRET_KEY = "random"`

  Windows: `setx APP_SECRET_KEY "random"`

- Run Flask App

  `python3 app.py`

- Open 127.0.0.1:5000 on your browser.

# Features

- Coming Soon

# Demo Site

The App is hosted at [https://linkrot-temp.herokuapp.com/](https://linkrot-temp.herokuapp.com/) during development.

# License

This program is licensed with an [MIT License](https://github.com/marshalmiller/linkrot/blob/main/LICENSE).
