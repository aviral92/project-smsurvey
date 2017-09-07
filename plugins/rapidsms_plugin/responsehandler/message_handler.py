import json

from rapidsms.router import send, lookup_connections
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from responsehandler.models import ParticipantModel


@csrf_exempt
def handle(request):

    body = json.loads(request.body.decode())

    instance_id = int(body['instance_id'])
    message = str(body['message'])
    participant = ParticipantModel.objects.get(instance_id=instance_id)

    send(message, lookup_connections(backend='twilio-backend', identities=[participant.phone_number]))

    return HttpResponse()
