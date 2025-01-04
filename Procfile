web: gunicorn --bind :8000 --workers 3 --threads 2 binary_product.wsgi:application
worker: celery -A binary_product worker --loglevel=info
beat: celery -A binary_product beat --loglevel=info