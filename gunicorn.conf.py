# Gunicorn configuration file for Stream Recorder Web UI
# This file uses relative paths and will work in any deployment location

import os
import multiprocessing

# Get the directory containing this config file (project root)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = min(4, multiprocessing.cpu_count() * 2 + 1)
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = os.path.join(LOGS_DIR, "gunicorn_access.log")
errorlog = os.path.join(LOGS_DIR, "gunicorn_error.log")
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "stream_recorder_web"

# Server mechanics
daemon = False  # Set to False when using systemd
pidfile = os.path.join(LOGS_DIR, "gunicorn.pid")
user = None  # Will be set by systemd service
group = None  # Will be set by systemd service
tmp_upload_dir = None

# SSL (uncomment and configure if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment
raw_env = [
    'FLASK_ENV=production',
    'PORT=8000',
]

# Application
wsgi_module = "main:app"
