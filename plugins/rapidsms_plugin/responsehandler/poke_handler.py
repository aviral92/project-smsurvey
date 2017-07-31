import requests
import os
import base64
import json

from .app import SurveyStarter

from django.http import HttpResponse

token = os.environ.get("SEC_TOKEN")
owner = os.environ.get("OWNER_NAME")
domain = os.environ.get("OWNER_DOMAIN")
url = os.environ.get("SYSTEM_URL")


def handle(request):
    plugin_id = request.POST.get('plugin_id')
    survey_id = request.POST.get('survey_id')
    a = owner + "@" + domain + "-" + plugin_id + ":" + token

    b64 = base64.b64encode(a.encode()).decode()
    headers = {
        "Authorization": "Basic " + b64
    }

    r = requests.get(url + "instance?survey_id=" + survey_id + "&status=not_started", headers=headers)
    response = json.loads(r.text)

    for iid in response['ids']:
        SurveyStarter.start_survey(survey_id, iid)

    return HttpResponse()