from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def handle(request):
    return JsonResponse({
        "name": "SMS",
        "icon": "fa-phone-square",
        "permissions": "2112334111"
    }, status=200)
