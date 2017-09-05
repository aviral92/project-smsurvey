import requests
import base64
import json

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from enrollments.models import OwnerModel, EnrollmentModel


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

    try:
        r = requests.get(url + "/enrollments", headers=headers)
        enrollments = json.loads(r.text)

        for enrollment in enrollments:
            e = EnrollmentModel.objects.filter(enrollment_id=enrollment['id']).first()

            if e is not None:
                e.delete()

            e = EnrollmentModel(owner_id=owner_id, plugin_id=plugin_id, enrollment_id=enrollment['id'],
                                enrollment_name=enrollment['name'], open_date=enrollment['open_date'],
                                close_date=enrollment['close_date'], expiry_date=enrollment['expiry_date'])
            e.save()
    except:
        return render(
            request,
            "enrollments/config.html",
            context={
                "status": "error",
                "enrollments": [],
                "plugin_id": plugin_id
            }
        )
    else:
        return render(
            request,
            "enrollments/config.html",
            context={
                "status": "success",
                "enrollments": enrollments
            }
        )
