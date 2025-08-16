release: python manage.py migrate && python manage.py setup_onep
web: gunicorn ONEP_ORG.wsgi:application --log-file -
