#!/bin/sh
set -e

poetry run alembic upgrade head

poetry run uvicorn --host 0.0.0.0 --port 8000 mars_probe_api.app:app
