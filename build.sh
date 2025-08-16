#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Set up initial data (creates superuser and sample products)
# First try to load from fixture, if not available create new data
python manage.py setup_onep --use-fixture
