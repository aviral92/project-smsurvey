import requests
import base64
import json
import pytz
import os

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware

from dateutil import parser

from enrollments.models import EnrollmentModel, OwnerModel


@csrf_exempt
def handle(request):

    if request.method == 'GET':
        return do_get(request)
    elif request.method == 'POST':
        return do_post(request)
    elif request.method == 'DELETE':
        return do_delete(request)
    else:
        return HttpResponse(status=405)


def do_get(request):
    enrollment_id = request.GET.get("enrollment_id")
    e = EnrollmentModel.objects.get(enrollment_id=enrollment_id)

    if e.open_date is not None:
        open_date = e.open_date.strftime("%Y-%m-%d")
    else:
        open_date = None

    if e.close_date is not None:
        close_date = e.close_date.strftime("%Y-%m-%d")
    else:
        close_date = None

    if e.expiry_date is not None:
        expiry_date = e.expiry_date.strftime("%Y-%m-%d")
    else:
        expiry_date = None

    url = os.environ.get("SYSTEM_URL") + '/enroll?enrollment_id=' + str(enrollment_id)

    ed = {"id": e.enrollment_id, "name": e.enrollment_name, "open_date": open_date, "close_date": close_date,
          "expiry_date": expiry_date, "url": url}

    return JsonResponse(ed, status=200)


def do_post(request):
    enrollment_id = int(request.POST.get('id'))
    plugin_id = int(request.POST.get('plugin_id'))
    enrollment_name = str(request.POST.get('name'))
    open_date = make_aware(parser.parse(request.POST.get('open_date')), pytz.utc)
    close_date = make_aware(parser.parse(request.POST.get('close_date')), pytz.utc)
    expires = str(request.POST.get("expires"))

    if expires == 'True' or expires == 'true':
        expiry_date = make_aware(parser.parse(request.POST.get('expiry_date')), pytz.utc)

    else:
        expiry_date = None

    owner = OwnerModel.objects.get(plugin_id=plugin_id)

    e = EnrollmentModel.objects.filter(enrollment_id=enrollment_id).first()

    url = str(owner.url)

    owner_id = str(owner.owner_id)
    token = str(owner.token)

    a = owner_id + "-" + str(plugin_id) + ":" + token
    b64 = base64.b64encode(a.encode()).decode()

    headers = {
        "Authorization": "Basic " + b64
    }

    if e is None:  # New enrollment
        return do_post_new(enrollment_name, open_date, close_date, expiry_date, url, headers, owner, plugin_id)
    else:  # Updating enrollment
        return do_post_update(enrollment_name, open_date, close_date, expiry_date, url, enrollment_id, headers, e,owner,
                              plugin_id)


def do_post_new(enrollment_name, open_date, close_date, expiry_date, url, headers, owner, plugin_id):
    data = {
        "name": enrollment_name,
        "open_date": open_date,
        "close_date": close_date,
        "expiry_date": expiry_date
    }

    r = requests.post(url + "/enrollments", data=data, headers=headers)

    if r.status_code == 200:
        try:
            response = json.loads(r.text)
            enrollment_id = int(response["enrollment_id"])

            e = EnrollmentModel(owner_id=owner.owner_id, plugin_id=plugin_id, enrollment_id=enrollment_id,
                                enrollment_name=enrollment_name, open_date=open_date, close_date=close_date,
                                expiry_date=expiry_date)

            e.save()

            return HttpResponse(status=200)

        except (ValueError, KeyError) as e:
            return JsonResponse({
                "status": "error",
                "message": e.message
            }, status=400)
    else:
        return JsonResponse({
            "status": "error",
            "message": "System rejected enrollment"
        }, status=400)


def do_post_update(enrollment_name, open_date, close_date, expiry_date, url, enrollment_id, headers, e, owner,
                   plugin_id):
    data = {
        "name": enrollment_name,
        "open_date": open_date,
        "close_date": close_date,
        "expiry_date": expiry_date
    }

    r = requests.post(url + "/enrollments/" + str(enrollment_id), data=data, headers=headers)

    if r.status_code == 200:
        try:
            response = json.loads(r.text)

            if response["status"] == "success":
                e.delete()

                e = EnrollmentModel(owner_id=owner.owner_id, plugin_id=plugin_id, enrollment_id=enrollment_id,
                                    enrollment_name=enrollment_name, open_date=open_date, close_date=close_date,
                                    expiry_date=expiry_date)
                e.save()

                return HttpResponse(status=200)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Unexpected message from system"
                }, status=400)
        except (ValueError, KeyError) as e:
            return JsonResponse({
                "status": "error",
                "message": e.message
            }, status=400)
    else:
        return JsonResponse({
            "status": "error",
            "message": "System rejected enrollment update"
        }, status=400)


def do_delete(request):

    body = request.body.decode()
    first_eq = body.find('=')
    amper = body.find('&')
    second_eq = body.rfind('=')
    plugin_id = int(body[first_eq + 1: amper])
    enrollment_id = int(body[second_eq + 1:])

    enrollment = EnrollmentModel.objects.get(enrollment_id=enrollment_id)

    if enrollment.plugin_id == plugin_id:
        owner = OwnerModel.objects.get(plugin_id=plugin_id)
        url = str(owner.url)
        owner_id = str(owner.owner_id)
        token = str(owner.token)

        a = owner_id + "-" + str(plugin_id) + ":" + token
        b64 = base64.b64encode(a.encode()).decode()

        headers = {
            "Authorization": "Basic " + b64
        }

        r = requests.delete(url + "/enrollments/" + str(enrollment_id), headers=headers)

        if r.status_code == 200:
            return HttpResponse(status=200)
        else:
            return JsonResponse({
                "status": "error",
                "message": "Server rejected deletion, ensure credentials are correct"
                }, status=400)
    else:
        return JsonResponse({
            "status": "error",
            "message": "Enrollment is not associated with owner"
        }, status=401)
