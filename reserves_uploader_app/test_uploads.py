"""Checks file uploads and the version view with the pinned dependencies."""

import json
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import SimpleTestCase, override_settings


class UploadTests(SimpleTestCase):
    def test_upload_and_repeated_filename(self) -> None:
        """Checks that uploading a repeated filename preserves both files and returns a link."""
        with ExitStack() as stack:
            directory = stack.enter_context(TemporaryDirectory(prefix='reserves-upload-'))
            stack.enter_context(
                override_settings(UPLOADS_DIR_PATH=directory, UPLOADS_DIR_URL_ROOT='https://uploads.example.invalid')
            )
            stack.enter_context(
                patch(
                    'reserves_uploader_app.lib.uploader_helper.prep_pattern_header_html',
                    return_value='<header>Test</header>',
                )
            )
            page = self.client.get('/uploader/')
            self.assertContains(page, '<header>Test</header>')
            for content in (b'%PDF-first', b'%PDF-second'):
                response = self.client.post(
                    '/uploader/',
                    {'file': SimpleUploadedFile('1234567890.pdf', content, content_type='application/pdf')},
                    follow=True,
                )
                self.assertContains(response, 'File uploaded; link:')
                self.assertContains(response, 'https://uploads.example.invalid/12/34/')
            files = list((Path(directory) / '12' / '34').glob('*.pdf'))
            self.assertEqual(len(files), 2)
            self.assertEqual({path.read_bytes() for path in files}, {b'%PDF-first', b'%PDF-second'})

    def test_version_view(self) -> None:
        """Checks that Trio can gather Git information for the version view."""
        response = self.client.get('/version/')
        assert isinstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content['response']['version'])
