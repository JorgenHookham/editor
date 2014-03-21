from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from django.utils import simplejson
import dropbox

def get_flow(request):
    callback_url = 'https://' + request.META['HTTP_HOST'] + reverse('authorize_callback')
    #session = cache.get('auth_csrf', {})

    #session = {}
    flow = dropbox.client.DropboxOAuth2Flow(settings.DROPBOX_API_KEY, settings.DROPBOX_API_SECRET, callback_url, request.session, 'dropbox-auth-csrf-token')
    #cache.set('auth_csrf', session)
    #print 'session: %s' % session
    #print 'cache.session: %s' % cache.get('auth_csrf', {})
    return flow

def authorize(request):
    authorize_url = get_flow(request).start()
    return HttpResponseRedirect(authorize_url)

def authorize_callback(request):
    code = request.GET['code']
    access_token, user_id, url_state = get_flow(request).finish(request.GET)
    request.session['access_token'] = access_token
    request.session['user_id'] = user_id
    return HttpResponseRedirect(reverse('home'))

def home(request):
    if not request.session.get('access_token'):
        return HttpResponseRedirect(reverse('authorize'))
    else:
        access_token = request.session['access_token']
        client = dropbox.client.DropboxClient(access_token)
        try:
            response = client.metadata('/Apps/Reporter-App/')
        except dropbox.rest.ErrorResponse:
            return HttpResponse('cannot find app!')
        response_encoded = simplejson.dumps(response)
        return HttpResponse(response_encoded, content_type='application/json')
