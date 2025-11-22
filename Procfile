web: gunicorn ${WSGI_MODULE}:application --bind 0.0.0.0:${PORT:-10000}

# Set the environment variable `WSGI_MODULE` in Render or your host to
# your Django project's WSGI module, for example: `myproject.wsgi`.