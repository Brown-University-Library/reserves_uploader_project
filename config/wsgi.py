"""Exposes the Django WSGI application using shared settings."""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

PROJECT_DIR_PATH = str(Path(__file__).resolve().parent.parent)
if PROJECT_DIR_PATH not in sys.path:
    sys.path.append(PROJECT_DIR_PATH)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
