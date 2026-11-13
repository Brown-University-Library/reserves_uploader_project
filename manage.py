#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """
    Runs management commands and isolates the test command from private settings.
    Called by: the script entry point.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            'available in the project environment? Run uv sync, then use '
            'uv run ./manage.py.'
        ) from exc
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        from config.testing import test_environment

        with test_environment():
            execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
