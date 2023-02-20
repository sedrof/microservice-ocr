#!/bin/bash

RUN_PORT=${PORT:-8001}

/usr/local/bin/gunicorn --worker-tmp-dir /tmp -k uvicorn.workers.UvicornWorker app.main:app --bind "0.0.0.0:${RUN_PORT}"
