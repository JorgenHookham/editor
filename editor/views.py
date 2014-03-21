from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.utils import simplejson
from django.shortcuts import redirect
from editor.utils import analyze_question
from editor.utils import build_pie_chart_data
from editor.utils import get_app_folder
from editor.utils import get_flow
import dropbox
import random
import string

def welcome(request):
    return redirect('authorize')

def authorize(request):
    authorize_url = get_flow(request).start()
    return HttpResponseRedirect(authorize_url)

def authorize_callback(request):
    code = request.GET['code']
    access_token, user_id, url_state = get_flow(request).finish(request.GET)

    # generate random key that we will tie to this access token
    key = ''.join(random.choice(string.ascii_uppercase) for i in range(20))

    # store reference to access token associated with key
    cache.set('key_%s_access_token' % key, access_token)

    # redirect to 'home'
    return redirect('authenticated_home', key=key)

def authenticated_home(request, key):
    access_token = cache.get('key_%s_access_token' % key)
    if not access_token:
        return redirect('welcome')
    else:
        client = dropbox.client.DropboxClient(access_token)
        return HttpResponse('hello', content_type='text/plain')

def pie_chart(request, key):
    question = request.GET['question']
    access_token = cache.get('key_%s_access_token' % key)
    client = dropbox.client.DropboxClient(access_token)
    data = analyze_question(client, question)
    pie_data = build_pie_chart_data(data)
    return HttpResponse(simplejson.dumps(pie_data), content_type='application/json')

