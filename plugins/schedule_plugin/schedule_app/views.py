import requests
import base64
import json

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from schedule_app.models import OwnerModel

@xframe_options_exempt
def config(request):
    """
    View function of the config page
    :param request:
    :return:
    """

    plugin_id = str(request.GET.get('plugin_id'))
    owner = OwnerModel.objects.get(plugin_id=plugin_id)
    url = str(owner.url)
    owner_id = str(owner.owner_id)
    token = str(owner.token)

    a = owner_id + "-" + plugin_id + ":" + token
    b64 = base64.b64encode(a.encode()).decode()

    headers = {
        "Authorization": "Basic " + b64
    }

    tasks = []
    protocols = []

    try:
        r = requests.get(url + "/tasks", headers=headers)
        tasks = json.loads(r.text)["tasks"]

        r = requests.get(url + "/protocols", headers=headers)
        protocols = json.loads(r.text)["protocols"]
    except Exception as e:
        return render(
            request,
            "schedule/config.html",
            context={
                "status": "error",
                "tasks": tasks,
                "plugin_id": plugin_id,
                "protocols": protocols,
                "message": str(e)
            }
        )
    else:
        return render(
            request,
            "schedule/config.html",
            context={
                "status": "success",
                "tasks": tasks,
                "plugin_id": plugin_id,
                "protocol": protocols
            }
        )
