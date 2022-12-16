import json, logging

from django.conf import settings as project_settings
from django.test import SimpleTestCase as TestCase  # `from django.test import TestCase` requires db
from django.test.utils import override_settings
from reserves_uploader_app.lib import pather


log = logging.getLogger(__name__)
TestCase.maxDiff = 1000


class PathsTest( TestCase ):
    """ Checks paths. """

    def setUp(self) -> None:
        self.file_names_to_test = [ 
            '1234567890.pdf',   # normal        # simple happy path
            'iñtërnâtiônàlĭzætiøn.pdf',         # unicode
            '.abcdef.txt',                      # eliminate leading dot
            ' qabcdef.txt',                     # eliminate leading space
            '. bcdef.txt',                      # eliminate leading dot and space
            'cde.txt',                          # handle short filename
            'de.txt',                           # handle shorter filename
            'f.txt',                            # handle shortest filename
            'gh ij kl.txt',                     # replace spaces with underscores
        ]

    def test_filenames_multiple(self):
        """ Checks filenames in bulk. """
        expected = [
            {'valid': True, 'err': None},
            {'valid': True, 'err': None},
        ]
        for i, file_name in enumerate( self.file_names_to_test ):
            result = pather.is_valid_filename(file_name)
            self.assertEqual( 
                expected[i], result, 
                f'failed on filename, ``{file_name}``; got, ``{result}``'   # only shows on failure
                )


    # def test_paths(self):
    #     """ Checks paths. """
    #     root_path = '/path/to/files'
    #     self.assertEqual(
    #         '/path/to/files/12/34/1234567890.pdf',
    #         pather.create_file_path( '1234567890.pdf', root_path ) 
    #     )

    # def test_paths_multiple(self):
    #     """ Checks paths in bulk. 
    #         TODO: add a challenging unicode-normalization entry. """
    #     root_path = '/path/to/files'
    #     file_names = [ 
    #         '1234567890.pdf',   # normal        # simple happy path
    #         'iñtërnâtiônàlĭzætiøn.pdf',         # unicode
    #         '.abcdef.txt',                      # eliminate leading dot
    #         ' qabcdef.txt',                     # eliminate leading space
    #         '. bcdef.txt',                      # eliminate leading dot and space
    #         'cde.txt',                          # handle short filename
    #         'de.txt',                           # handle shorter filename
    #         'f.txt',                            # handle shortest filename
    #         'gh ij kl.txt',                     # replace spaces with underscores
    #     ]
    #     expected = [
    #         '/path/to/files/12/34/1234567890.pdf',
    #         '/path/to/files/iñ/të/iñtërnâtiônàlĭzætiøn.pdf',
    #         '/path/to/files/ab/cd/abcdef.txt',
    #         '/path/to/files/qa/bc/qabcdef.txt',
    #         '/path/to/files/bc/de/bcdef.txt',
    #         'z/path/to/files/cd/cde.txt',
    #         'zz/path/to/files/de.txt',
    #         'zzz/path/to/files/f.txt',
    #         'zzzz/path/to/files/gh/_i/gh_ij_kl.txt'
    #     ]
    #     for i, file_name in enumerate(file_names):
    #         self.assertEqual( expected[i], pather.create_file_path( file_name, root_path )    
    #     )


class ErrorCheckTest( TestCase ):
    """ Checks urls. """

    @override_settings(DEBUG=True)  # for tests, DEBUG autosets to False
    def test_dev_errorcheck(self):
        """ Checks that dev error_check url triggers error.. """
        log.debug( f'debug, ``{project_settings.DEBUG}``' )
        try:
            log.debug( 'about to initiate client.get()' )
            response = self.client.get( '/error_check/' )
        except Exception as e:
            log.debug( f'e, ``{repr(e)}``' )
            self.assertEqual( "Exception('Raising intentional exception.')", repr(e) )

    def test_prod_errorcheck(self):
        """ Checks that production error_check url returns 404. """
        log.debug( f'debug, ``{project_settings.DEBUG}``' )
        response = self.client.get( '/error_check/' )
        self.assertEqual( 404, response.status_code )
