"""
WSGI config for Cloud project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cloud.settings')

application = get_wsgi_application()

# Optionally enable WhiteNoise for serving static files when available.
try:
	from whitenoise import WhiteNoise
	# static files are collected to BASE_DIR/staticfiles by settings.STATIC_ROOT
	static_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')
	application = WhiteNoise(application, root=static_root)
except Exception:
	# If whitenoise is not installed in the environment, continue without it.
	pass
