from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def handle(request):
    return JsonResponse({
        "name": "Enrollments",
        "icon": "fa-child",
        "permissions": "4411111121"
    }, status=200)
