from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from django.utils import simplejson
import dropbox
from dateutil import parser

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
        file_data = get_last_reporter_export(client)
        
        return HttpResponse(file_data, content_type='text/plain')
        #response_encoded = simplejson.dumps(last_response)
        #return HttpResponse(response_encoded, content_type='application/json')

def tired_pie_chart(request):
    pie_data = { 
        "item": [ 
            { 
                "value": "100", 
                "label": "May", 
                "colour": "FFFF10AA" 
                }, 
            { 
                "value": "160", 
                "label": "June", 
                "colour": "FFAA0AAA" 
                }, 
            { 
                "value": "300", 
                "label": "July", 
                "colour": "FF5505AA" 
                }, 
            { 
                "value": "140", 
                "label": "August", 
                "colour": "FF0000AA" 
                } 
            ] 
    }
    return HttpResponse(simplejson.dumps(pie_data), content_type='application/json')


#### UTILS #####
def get_last_reporter_export(client):
    app_folder = get_app_folder(client)
    last_response = get_last_file(app_folder)
    return get_file_content(client, last_response)


def get_app_folder(client):
    try:
        return client.metadata('/Apps/Reporter-App/')
    except dropbox.rest.ErrorResponse:
        raise Exception('Reporter app not linked on Dropbox')

def get_last_file(folder):
    last_file = None
    for file_metadata in folder['contents']:
        if not last_file:
            last_file = file_metadata
        elif parser.parse(file_metadata['modified']) > parser.parse(last_file['modified']):
            last_file = file_metadata
    return last_file
        
def get_file_content(client, file_metadata):
    f, metadata = client.get_file_and_metadata(file_metadata['path'])
    return f.read()

def get_flow(request):
    callback_url = 'https://' + request.META['HTTP_HOST'] + reverse('authorize_callback')
    flow = dropbox.client.DropboxOAuth2Flow(settings.DROPBOX_API_KEY, settings.DROPBOX_API_SECRET, callback_url, request.session, 'dropbox-auth-csrf-token')
    return flow


