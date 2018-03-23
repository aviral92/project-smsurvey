import requests
import base64

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from schedule_app.models import OwnerModel


@csrf_exempt
def handle(request):

    if request.method == 'GET':
        return do_get(request)
    if request.method == 'POST':
        return do_post(request)
    elif request.method == 'DELETE':
        return do_delete(request)
    else:
        return HttpResponse(status=405)


def do_get(request):

    try:
        task_id = str(request.GET.get("task_id"))
        plugin_id = int(request.GET.get("plugin_id"))
    except (KeyError, ValueError):
        return JsonResponse({
            "status": "error",
            "message": "Missing or ill-formatted parameter"
        })

    owner = OwnerModel.objects.get(plugin_id=plugin_id)
    url = str(owner.url)
    owner_id = str(owner.owner_id)
    token = str(owner.token)

    a = owner_id + "-" + str(plugin_id) + ":" + token
    b64 = base64.b64encode(a.encode()).decode()

    headers = {
        "Authorization": "Basic " + b64
    }

    get = requests.get(url + "/tasks/" + task_id, headers=headers)

    if get.status_code != 200:
        return JsonResponse({
            "status": "error",
            "message": get.json()["message"]
        }, status=get.status_code)
    else:
        return JsonResponse(get.json(), status=200)


def do_post(request):

    try:
        plugin_id = request.POST.get("plugin_id")
        name = request.POST.get("name")
        protocol_id = request.POST.get("protocol_id")
        enrollment_id = request.POST.get("enrollment_id")
        timezone = request.POST.get("timezone")
        time_rule = request.POST.get("time_rule")
        enable_notes = request.POST.get("enable_notes")
        timeout = request.POST.get("timeout")
        enable_warnings = request.POST.get("enable_warnings")
        print(timezone)
    except KeyError:
        return JsonResponse({
            "status": "error",
            "message": "Missing parameter"
        }, status=400)
    print(time_rule)
    owner = OwnerModel.objects.get(plugin_id=int(plugin_id))

    url = str(owner.url)

    owner_id = str(owner.owner_id)
    token = str(owner.token)

    a = owner_id + "-" + str(plugin_id) + ":" + token
    b64 = base64.b64encode(a.encode()).decode()

    headers = {
        "Authorization": "Basic " + b64
    }

    data = {
        "name": name,
        "protocol_id": protocol_id,
        "enrollment_id": enrollment_id,
        "time_rule": time_rule,
        "enable_notes": enable_notes,
        "timeout": timeout,
        "enable_warnings": enable_warnings
    }

    post = requests.post(url + "/tasks", data=data, headers=headers)

    if post.status_code != 200:
        return JsonResponse({
            "status": "error",
            "message": post.json()["message"]
        }, status=post.status_code)
    else:
        return HttpResponse(200)


def do_delete(request):
    body = request.body.decode()
    first_eq = body.find('=')
    amper = body.find('&')
    second_eq = body.rfind('=')
    plugin_id = int(body[first_eq + 1: amper])
    task_id = int(body[second_eq + 1:])

    owner = OwnerModel.objects.get(plugin_id=int(plugin_id))

    url = str(owner.url)

    owner_id = str(owner.owner_id)
    token = str(owner.token)

    a = owner_id + "-" + str(plugin_id) + ":" + token
    b64 = base64.b64encode(a.encode()).decode()

    headers = {
        "Authorization": "Basic " + b64
    }

    delete = requests.delete(url + "/tasks/" + str(task_id), headers=headers)

    if delete.status_code != 200:
        return JsonResponse({
            "status": "error",
            "message": delete.json()["message"]
        }, status=delete.status_code)
    else:
        return HttpResponse(200)
