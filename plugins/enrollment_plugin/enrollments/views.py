import requests
import base64
import json
import pytz

from dateutil import parser

from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.timezone import make_aware

from enrollments.models import OwnerModel, EnrollmentModel


def enroll(request):
    enrollment_id = int(request.GET.get('enrollment_id'))
    enrollment = EnrollmentModel.objects.get(enrollment_id=enrollment_id)

    plugin_id = enrollment.plugin_id
    owner = OwnerModel.objects.get(plugin_id=plugin_id)
    url = str(owner.url)
    owner_id = str(owner.owner_id)
    token = str(owner.token)

    a = owner_id + "-" + str(plugin_id) + ":" + token
    b64 = base64.b64encode(a.encode()).decode()

    headers = {
        "Authorization": "Basic " + b64
    }

    get = requests.get(url + '/plugins?permissions=2112331111', headers=headers)
    get_json = get.json()

    return render(
        request,
        "enrollments/enroll.html",
        context= {
            "enrollment": {
                "id": enrollment_id,
                "name": str(enrollment.enrollment_name),
            },
            "plugins": get_json["plugins"]
        }
    )


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
        enrollments = json.loads(r.text)["enrollments"]

        for enrollment in enrollments:
            e = EnrollmentModel.objects.filter(enrollment_id=enrollment['id']).first()

            if e is not None:
                e.delete()

            if enrollment['open_date'] is not None:
                open_date = make_aware(parser.parse(enrollment['open_date']), timezone=pytz.utc)
            else:
                open_date = None

            if enrollment['close_date'] is not None:
                close_date = make_aware(parser.parse(enrollment["close_date"]), timezone=pytz.utc)
            else:
                close_date = None

            if enrollment['expiry_date'] is not None:
                expiry_date = make_aware(parser.parse(enrollment["expiry_date"]), timezone=pytz.utc)
            else:
                expiry_date = None

            e = EnrollmentModel(owner_id=owner_id, plugin_id=plugin_id, enrollment_id=enrollment['id'],
                                enrollment_name=enrollment['name'], open_date=open_date,
                                close_date=close_date, expiry_date=expiry_date)
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
                "enrollments": enrollments,
                "plugin_id": plugin_id
            }
        )
