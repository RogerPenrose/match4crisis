import multiprocessing
import os

from django.conf import settings

bind = "backend:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000

accesslog = os.path.join(settings.RUN_DIR, "gunicorn-access.log")
access_log_format = '%(t)s|"%(r)s"|%(s)s|%(T)s'
