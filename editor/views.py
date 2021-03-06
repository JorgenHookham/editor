from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.utils import simplejson
from django.shortcuts import redirect
from editor.models import DropboxAccessToken
from editor.utils import count_question_answers
from editor.utils import count_question_numeric_response_by_day
from editor.utils import build_counter_data
from editor.utils import build_pie_chart_data
from editor.utils import build_line_chart_data
from editor.utils import count_reports
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
    access_token = DropboxAccessToken.objects.create(key=key,access_token=access_token)

    # redirect to 'home'
    return redirect('authenticated_home', key=key)

def authenticated_home(request, key):
    access_token = DropboxAccessToken.objects.get(key=key).access_token
    client = dropbox.client.DropboxClient(access_token)
    return HttpResponse('hello', content_type='text/plain')

def pie_chart(request, key):
    question = request.GET['question']
    num_days = int(request.GET.get('days', 5))
    access_token = DropboxAccessToken.objects.get(key=key).access_token
    client = dropbox.client.DropboxClient(access_token)
    data = count_question_answers(client, question, num_days)
    pie_data = build_pie_chart_data(data)
    return HttpResponse(simplejson.dumps(pie_data), content_type='application/json')

def line_chart(request, key):
    question = request.GET['question']
    num_days = int(request.GET.get('days', 5))
    access_token = DropboxAccessToken.objects.get(key=key).access_token
    client = dropbox.client.DropboxClient(access_token)
    data = count_question_numeric_response_by_day(client, question, num_days)
    line_data = build_line_chart_data(data)
    return HttpResponse(simplejson.dumps(line_data), content_type='application/json')

def report_counter(request, key):
    """
    Returns the number of reports made in a period of time.
    """
    num_days = int(request.GET.get('days', 5))
    access_token = DropboxAccessToken.objects.get(key=key).access_token
    client = dropbox.client.DropboxClient(access_token)
    data = count_reports(client, num_days)
    counter_data = build_counter_data(data)
    return HttpResponse(simplejson.dumps(counter_data), content_type='application/json')



