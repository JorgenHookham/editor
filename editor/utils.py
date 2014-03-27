from collections import Counter
from dateutil import parser
from datetime import date
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import simplejson
import dropbox
import os
import re

def count_question_answers(client, question, num_days=None):
    counts = Counter()

    files = get_app_folder_by_date(client)
    if num_days:
        files = files[-1 * num_days:]

    for file_metadata in files:
        content = get_file_content(client, file_metadata)
        content = simplejson.loads(content)
        for snapshot in content['snapshots']:
            for response in snapshot['responses']:
                if response['questionPrompt'].lower() == question.lower():
                    choices = response.get('answeredOptions') or response.get('tokens') or []
                    for answered_option in choices:
                        counts[answered_option] += 1
    return counts

def count_question_numeric_response_by_day(client, question, num_days=None):
    #return [1,2,3,4,5,6]

    data = []

    files = get_app_folder_by_date(client)
    if num_days:
        files = files[-1 * num_days:]

    for file_metadata in files:
        content = get_file_content(client, file_metadata)
        content = simplejson.loads(content)

        day_value = 0

        for snapshot in content['snapshots']:
            for response in snapshot['responses']:
                if response['questionPrompt'].lower() == question.lower():
                    day_value += float(response['numericResponse'])

        data.append(day_value)

    return data

def count_reports(client, num_days=1):
  """
  Counts the number of reports made in a period of time. Assumes that a snapshot
  is synonymous with report.
  """
  count = 0
  files = get_app_folder_by_date(client)[-1 * num_days:]
  for file_metadata in files:
    content = get_file_content(client, file_metadata)
    content = simplejson.loads(content)
    if 'snapshots' in content:
      for snapshot in content['snapshots']:
        count += 1
  return count

def build_pie_chart_data(data_dict):
    colors = ["D71E15","E76517","FEB01B","FECB1B","FEDF74","FF5E49","FAAE0D","FDFBC8"]
    pie_items = []
    for index, key in enumerate(data_dict.keys()):
        pie_items.append({'label':key,'value':data_dict[key],'color':colors[index]})
    return {'item':pie_items}

def build_line_chart_data(data_list):
    data = {
        "item": data_list,
        "settings": {
            "axisx": [
                "%d Days Ago" % (len(data_list) - 1),
                "%d Days Ago" % ((len(data_list) - 1) / 2),
                "Today"
            ],
            "axisy": [min(data_list), max(data_list)],
            "colour": "ff9900"
        }
    }
    return data

def get_app_folder(client):
    """
    Get all the files in the reporter export folder
    """
    try:
        return client.metadata('/Apps/Reporter-App/')['contents']
    except dropbox.rest.ErrorResponse:
        raise Exception('Reporter app not linked on Dropbox')

def get_app_folder_by_date(client):
    """
    Get all files in the reporter export folder, sorted by date; earliest files go first, latest go last
    """
    files = get_app_folder(client)

    def get_file_date(file_metadata):
        # reporter exports follow a YYYY-MM-DD-filename structure, which we use to extract the associated date and build a date object
        # we cannot use the modified metadata, as it may reflect the date all the data was exported to dropbox rather than the recording date
        filename = os.path.basename(file_metadata['path'])
        results = re.search('^(\d+)-(\d+)-(\d+)-.+', filename)
        date_created = date(int(results.group(1)),int(results.group(2)),int(results.group(3)))
        return date_created

    files.sort(key=get_file_date)

    return files

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

