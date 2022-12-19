#!/usr/bin/env sh

gunicorn --bind 0.0.0.0:5000 --workers 3 --worker-class gevent --max-requests 1000 --timeout 30 --error-logfile error.log "project:create_app()"
