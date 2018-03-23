import base64
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from enrollments.models import OwnerModel, EnrollmentModel


@csrf_exempt
def handle(request):

    participant_plugin_id = int(request.POST.get("plugin_id"))
    plugin_scratch = str(request.POST.get("plugin_scratch"))
    plugin_name = str(request.POST.get("plugin_name"))
    enrollment_id = int(request.POST.get("enrollment_id"))

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

    data = {
        "plugin_id": participant_plugin_id,
        "plugin_name": plugin_name,
        "plugin_scratch": plugin_scratch
    }

    post = requests.post(url + '/enrollments/' + str(enrollment_id) + '/enrolled', data=data, headers=headers)

    if post.status_code == 200:
        try:
            post_json = post.json()

            if post_json["status"] == "success":
                return JsonResponse({
                    "status": "success"
                }, status=200)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": post_json["message"]
                }, status=400)
        except (ValueError, KeyError) as e:
            return JsonResponse({
                "status": "error",
                "message": e.message
            }, status=400)
    else:
        return JsonResponse({
            "status": "error",
            "message": "Error from system"
        }, status=400)

