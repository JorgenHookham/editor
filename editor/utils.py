from collections import Counter
from dateutil import parser
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import simplejson
import dropbox

def analyze_question(client, question):
    counts = Counter()
    for file_metadata in get_app_folder(client)['contents']:
        content = get_file_content(client, file_metadata)
        content = simplejson.loads(content)
        for snapshot in content['snapshots']:
            for response in snapshot['responses']:
                if response['questionPrompt'].lower() == question.lower():
                    choices = response.get('answeredOptions') or response.get('tokens')
                    for answered_option in choices:
                        counts[answered_option] += 1
    return counts

def build_pie_chart_data(data_dict):
    colors = ["D71E15","E76517","FEB01B","FECB1B","FEDF74","FF5E49","FAAE0D","FDFBC8"]
    pie_items = []
    for index, key in enumerate(data_dict.keys()):
        pie_items.append({'label':key,'value':data_dict[key],'color':colors[index]})
    return {'item':pie_items}

def get_app_folder(client):
    try:
        return client.metadata('/Apps/Reporter-App/')
    except dropbox.rest.ErrorResponse:
        raise Exception('Reporter app not linked on Dropbox')

       
def get_file_content(client, file_metadata):
    f, metadata = client.get_file_and_metadata(file_metadata['path'])
    return f.read()

def get_flow(request):
    protocol = 'http' if 'localhost' in request.META['HTTP_HOST'] else 'https'
    callback_url = '%s://%s%s' % (protocol, request.META['HTTP_HOST'], reverse('authorize_callback'))
    print settings.DROPBOX_API_SECRET
    flow = dropbox.client.DropboxOAuth2Flow(settings.DROPBOX_API_KEY, settings.DROPBOX_API_SECRET, callback_url, request.session, 'dropbox-auth-csrf-token')
    return flow

# Deprecated
def get_last_file(folder):
    last_file = None
    for file_metadata in folder['contents']:
        if not last_file:
            last_file = file_metadata
        elif parser.parse(file_metadata['modified']) > parser.parse(last_file['modified']):
            last_file = file_metadata
    return last_file
 
