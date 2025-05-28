web: gunicorn mycity.wsgi:application --bind 0.0.0.0:$PORT
daphne: daphne -b 0.0.0.0 -p 8001 mycity.asgi:application

