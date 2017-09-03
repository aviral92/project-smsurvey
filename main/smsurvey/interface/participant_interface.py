import base64
import json

from tornado.web import RequestHandler

from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.owner_service import OwnerService


def authenticate(response):
    auth = response.request.headers.get("Authorization")

    if auth is None:
        response.set_status(401)
        response.write('{"status":"error","message":"Missing Authorization header"}')
        response.flush()

    if auth.startswith("Basic"):
        base64enc = auth[6:]
        credentials = base64.b64decode(base64enc).decode()
        at_index = credentials.find("@")
        hyphen_index = credentials.find("-")
        colon_index = credentials.find(":")

        if colon_index is -1 or hyphen_index is -1 or at_index is -1:
            response.set_status(401)
            response.write('{"status":"error","message":"Invalid Authorization header"}')
            response.flush()
        else:
            owner = credentials[:hyphen_index]
            owner_name = owner[:at_index]
            owner_domain = owner[at_index + 1:]

            plugin_id = credentials[hyphen_index + 1: colon_index]
            token = credentials[colon_index + 1:]

            if PluginService.validate_plugin(plugin_id, owner_name, owner_domain, token):
                return {
                    "valid": True,
                    "owner_domain": owner_domain,
                    "owner_name": owner_name
                }
            else:
                response.set_status(403)
                response.write('{"status":"error","message":"Do not have authorization retrieve participant information}')
                response.flush()

    else:
        response.set_status(401)
        response.write('{"status":"error","message":"Invalid Authorization header - no basic"}')
        response.flush()

    return {"valid": False}


class ParticipantHandler(RequestHandler):

    # GET /participants?survey_id=<SURVEY_ID>&instance_id=<INSTANCE_ID> <- Should return participant for instance_id
    def get(self):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_id = self.get_argument("survey_id")
            instance_id = self.get_argument("instance_id")

            instance = InstanceService.get_instance(instance_id)
            survey = SurveyService.get_survey(survey_id)

            if instance is None or survey is None:
                response = {
                    "status": "error",
                    "message": "Invalid instance or survey ID"
                }

                self.set_status(400)
                self.write(json.dumps(response))
                self.flush()
            else:
                owner_id = survey.owner_id
                owner = OwnerService.get_by_id(owner_id)
                if owner.name == auth_response["owner_name"] and owner.domain == auth_response["owner_domain"]:

                    participant = ParticipantService.get_participant(instance.participant_id)

                    response = {
                        "status": "success",
                        "participant": participant.plugin_scratch,
                    }

                    self.set_status(200)
                    self.write(json.dumps(response))
                    self.flush()
                else:
                    response = {
                        "status": "error",
                        "message": "Do not have authorization to make this request"
                    }

                    self.set_status(401)
                    self.write(json.dumps(response))
                    self.flush()

    def data_received(self, chunk):
        pass
