"""Checks configuration loading without opening the real outer .env."""

import json
import os
import runpy
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase

from config.testing import test_environment


class EnvironmentSettingsTests(SimpleTestCase):
    def test_outer_file_location_precedence_and_literal_values(self) -> None:
        """Checks that settings find the outer file from an unrelated working directory."""
        source = Path(__file__).with_name('settings.py')
        with TemporaryDirectory(prefix='reserves-settings-') as temporary_directory:
            root = Path(temporary_directory).resolve()
            copied_settings = root / 'project' / 'config' / 'settings.py'
            copied_settings.parent.mkdir(parents=True)
            copied_settings.write_text(source.read_text())
            sample = (source.parent.parent / '.env.example').read_text()
            sample = sample.replace('local-development-only-change-before-other-use', 'literal-${KEEP_THIS}-value')
            (root / '.env').write_text(sample)
            unrelated = root / 'unrelated'
            unrelated.mkdir()
            (unrelated / '.env').write_text('RSRVS_UPLDR__SECRET_KEY=wrong-working-directory\n')
            environment = {key: value for key, value in os.environ.items() if not key.startswith('RSRVS_UPLDR__')}
            environment['RSRVS_UPLDR__SECRET_KEY'] = 'inherited-value'
            environment['KEEP_THIS'] = 'expanded-value'
            result = subprocess.run(
                [
                    sys.executable,
                    '-c',
                    (
                        'import json, runpy, sys; settings = runpy.run_path(sys.argv[1]); '
                        'print(json.dumps({key: settings[key] for key in '
                        '("SECRET_KEY", "SESSION_FILE_PATH", "STATIC_ROOT", "UPLOADS_DIR_PATH")}))'
                    ),
                    str(copied_settings),
                ],
                cwd=unrelated,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            settings = json.loads(result.stdout)
            self.assertEqual(settings['SECRET_KEY'], 'literal-${KEEP_THIS}-value')
            for key, directory in (
                ('SESSION_FILE_PATH', 'sessions'),
                ('STATIC_ROOT', 'static'),
                ('UPLOADS_DIR_PATH', 'uploads'),
            ):
                self.assertEqual(settings[key], str(root / 'local_data' / directory))

    def test_tests_never_load_dotenv(self) -> None:
        """Checks that test settings prevent dotenv from reading any file."""
        with test_environment(), patch('dotenv.load_dotenv', side_effect=AssertionError('Unexpected .env read')):
            settings = runpy.run_path(str(Path(__file__).with_name('settings.py')))
            self.assertEqual(settings['SECRET_KEY'], 'synthetic-test-key')
            self.assertTrue(Path(settings['SESSION_FILE_PATH']).is_dir())
            self.assertEqual(settings['EMAIL_HOST'], 'localhost')

    def test_temporary_storage_is_removed(self) -> None:
        """Checks that test storage is removed and inherited values are restored."""
        with patch.dict(os.environ, {'RSRVS_UPLDR__SECRET_KEY': 'inherited-synthetic-key'}):
            with test_environment():
                session_directory = Path(os.environ['RSRVS_UPLDR__SESSION_FILE_PATH'])
                self.assertTrue(session_directory.is_dir())
                self.assertEqual(os.environ['RSRVS_UPLDR__SECRET_KEY'], 'synthetic-test-key')
            self.assertFalse(session_directory.exists())
            self.assertEqual(os.environ['RSRVS_UPLDR__SECRET_KEY'], 'inherited-synthetic-key')
