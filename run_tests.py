#!/usr/bin/env python
"""
Runs Django tests with synthetic settings and temporary files.

Usage: uv run ./run_tests.py [test labels] [Django test options]
Example: uv run ./run_tests.py reserves_uploader_app.tests.PathsTest -v 2
"""

import sys

from django.core.management import execute_from_command_line

from config.testing import test_environment


def main() -> None:
    """
    Runs the requested tests without loading the outer .env.
    Called by: the script entry point.
    """
    with test_environment():
        execute_from_command_line(['manage.py', 'test', *sys.argv[1:]])


if __name__ == '__main__':
    main()
