# gunicorn_config.py
import multiprocessing

bind = "127.0.0.1:8000"   # bind the server to localhost at port 8000
workers = multiprocessing.cpu_count() * 2 + 1  # number of worker processes
threads = 2  # number of threads per worker
timeout = 120  # timeout in seconds
