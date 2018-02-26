import requests
import base64
import json

from .app import SurveyStarter

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from responsehandler.models import OwnerModel



@csrf_exempt
def handle(request):
    body = json.loads(request.body.decode())
    plugin_id = str(body['plugin_id'])
    survey_id = str(body['survey_id'])

    owner = OwnerModel.objects.get(plugin_id=plugin_id)

    owner_id = str(owner.owner_id)
    token = str(owner.token)
    url = str(owner.url)

    a = owner_id + "-" + plugin_id + ":" + token

    b64 = base64.b64encode(a.encode()).decode()
    headers = {
        "Authorization": "Basic " + b64
    }

    r = requests.get(url + "/instances?survey_id=" + survey_id + "&status=not_started", headers=headers)
    if r.status_code == 500:
        print("Error from system, giving up with request")
        return HttpResponse()

    response = json.loads(r.text)
    print("Response::", response)
    for iid in response['ids']:
        SurveyStarter.start_survey(plugin_id, owner_id, token, url, survey_id, iid)

    return HttpResponse()
