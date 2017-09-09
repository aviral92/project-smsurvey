from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def handle(request):
    return JsonResponse({
        "status": "healthy"
    },status=200)
