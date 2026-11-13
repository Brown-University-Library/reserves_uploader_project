"""Supplies temporary settings for tests without reading private configuration."""

import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator
from unittest.mock import patch


@contextmanager
def test_environment() -> Iterator[None]:
    """
    Supplies synthetic settings and temporary storage for the test process.
    Called by: run_tests.main(), manage.main(), and settings tests.
    """
    with TemporaryDirectory(prefix='reserves-tests-') as temporary_directory:
        root = Path(temporary_directory)
        for name in ('sessions', 'static', 'uploads'):
            (root / name).mkdir()
        environment = {key: value for key, value in os.environ.items() if not key.startswith('RSRVS_UPLDR__')}
        environment.update(
            {
                'DJANGO_SETTINGS_MODULE': 'config.settings',
                'RSRVS_UPLDR__TESTING': '1',
                'RSRVS_UPLDR__SECRET_KEY': 'synthetic-test-key',
                'RSRVS_UPLDR__DEBUG_JSON': 'false',
                'RSRVS_UPLDR__ADMINS_JSON': '[]',
                'RSRVS_UPLDR__ALLOWED_HOSTS_JSON': '["testserver", "localhost"]',
                'RSRVS_UPLDR__SESSION_FILE_PATH': str(root / 'sessions'),
                'RSRVS_UPLDR__STATIC_URL': '/static/',
                'RSRVS_UPLDR__STATIC_ROOT': str(root / 'static'),
                'RSRVS_UPLDR__SERVER_EMAIL': 'uploader@example.invalid',
                'RSRVS_UPLDR__EMAIL_HOST': 'localhost',
                'RSRVS_UPLDR__EMAIL_PORT': '1026',
                'RSRVS_UPLDR__LOG_PATH': str(root / 'tests.log'),
                'RSRVS_UPLDR__LOG_LEVEL': 'WARNING',
                'RSRVS_UPLDR__UPLOADS_DIR_PATH': str(root / 'uploads'),
                'RSRVS_UPLDR__UPLOADS_DIR_URL_ROOT': 'https://uploads.example.invalid',
                'RSRVS_UPLDR__PATTERN_LIB_HEADER_URL': 'https://header.example.invalid',
                'RSRVS_UPLDR__PATTERN_LIB_CACHE_TIMEOUT_IN_HOURS': '1',
            }
        )
        with patch.dict(os.environ, environment, clear=True):
            yield
