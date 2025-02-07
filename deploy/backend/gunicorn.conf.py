# gunicorn.conf.py
bind = "0.0.0.0:8000"
chdir = "/skg/backend/"
workers = 1
threads = 4
backlog = 512
timeout = 120
daemon = False
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 2000
pidfile = "/skg/gunicorn.pid"
accesslog = "/var/log/fastapi_server/gunicorn_access.log"
errorlog = "/var/log/fastapi_server/gunicorn_error.log"
capture_output = True
loglevel = "debug"
pythonpath = "/usr/local/lib/python3.10/site-packages"
