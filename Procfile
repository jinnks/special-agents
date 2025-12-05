web: cd backend && python3 migrate_schema_v2.py && gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - 'app:create_app()'
