import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from enrollments.models import OwnerModel


@csrf_exempt
def handle(request):

    body = json.loads(request.body.decode())
    owner_id = body["owner_id"]
    plugin_id = body["plugin_id"]
    token = body["token"]
    url = body["url"]

    o = OwnerModel(owner_id=int(owner_id), plugin_id=int(plugin_id), token=str(token), url=str(url))
    o.save()

    print("Registered owner " + str(owner_id))

    return JsonResponse({
        "status": "success"
    },status=200)
