import datetime, json, logging, pprint

import trio
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from reserves_uploader_app.forms import UploadFileForm
from reserves_uploader_app.lib import version_helper
from reserves_uploader_app.lib.version_helper import GatherCommitAndBranchData

log = logging.getLogger(__name__)


# -------------------------------------------------------------------
# main urls
# -------------------------------------------------------------------

# def uploader( request ):
#     """ On GET, return the uploader page.
#         On POST, process the uploaded file via django chunked-upload. """
#     log.debug( 'starting' )
#     if request.method == 'POST':
#         log.debug( 'request.POST, ``%s``' % request.POST )
#         log.debug( 'request.FILES, ``%s``' % request.FILES )
#         return HttpResponse( 'Thanks for the upload!' )
#     else:
#         return render( request, 'reserves_uploader_app/uploader.html' )


def info(request):
    return HttpResponse( "Hello, world." )


@ensure_csrf_cookie
def uploader(request):
    log.debug( 'starting uploader()' )
    if request.method == 'POST':
        log.debug( 'POST detected' )
        log.debug( f'request.POST, ``{pprint.pformat(request.POST)}``' )
        log.debug( f'request.FILES, ``{pprint.pformat(request.FILES)}``' )
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file( request.FILES['file'] )
            context = {'msg' : '<span style="color: green;">File successfully uploaded</span>'}
            return render(request, 'templates/single_file.html', context)
        else:
            log.debug( 'form not valid' )
    else:
        log.debug( 'not POST detected' )
        form = UploadFileForm()
    return render(request, 'templates/single_file.html', {'form': form})

def handle_uploaded_file(f):
    log.debug( f'f.__dict__, ``{pprint.pformat(f.__dict__)}``' )
    full_file_path = f'{settings.UPLOADS_DIR_PATH}/{f.name}'
    with open( full_file_path, 'wb+' ) as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    log.debug( f'writing finished' )
    return





# -------------------------------------------------------------------
# support urls
# -------------------------------------------------------------------


def error_check( request ):
    """ For an easy way to check that admins receive error-emails (in development)...
        To view error-emails in runserver-development:
        - run, in another terminal window: `python -m smtpd -n -c DebuggingServer localhost:1026`,
        - (or substitue your own settings for localhost:1026)
    """
    log.debug( f'settings.DEBUG, ``{settings.DEBUG}``' )
    if settings.DEBUG == True:
        log.debug( 'triggering exception' )
        raise Exception( 'Raising intentional exception.' )
    else:
        log.debug( 'returing 404' )
        return HttpResponseNotFound( '<div>404 / Not Found</div>' )


def version( request ):
    """ Returns basic branch and commit data. """
    rq_now = datetime.datetime.now()
    gatherer = GatherCommitAndBranchData()
    trio.run( gatherer.manage_git_calls )
    commit = gatherer.commit
    branch = gatherer.branch
    info_txt = commit.replace( 'commit', branch )
    context = version_helper.make_context( request, rq_now, info_txt )
    output = json.dumps( context, sort_keys=True, indent=2 )
    log.debug( f'output, ``{output}``' )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


def root( request ):
    return HttpResponseRedirect( reverse('info_url') )
