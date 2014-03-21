from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
import dropbox

def get_flow(request):
    callback_url = 'https://' + request.HTTP_HOST + reverse('authorize_callback')
    return dropbox.client.DropboxOAuth2Flow(settings.DROPBOX_API_KEY, settings.DROPBOX_API_SECRET, callback_url, request.session, 'dropbox-auth-csrf-token')

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
    return HttpResponse(request.session['access_token'])