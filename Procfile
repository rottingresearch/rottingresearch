web: gunicorn app:app --timeout 1200
worker: python worker.py
newrelic-admin run-program gunicorn -b "0.0.0.0:$PORT" -w 3 --chdir datacrunch-consulting webserver:flaskapp
