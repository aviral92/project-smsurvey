from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def handle(request):
    return JsonResponse({
        "name": "Scheduling",
        "icon": "fa-calendar",
        "permissions": "1221111411"
    }, status=200)
