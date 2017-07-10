import base64
import json

from tornado.web import RequestHandler

from smsurvey.core.services.survey_service import SurveyService
from smsurvey.interface.services.plugin_service import PluginService


def authenticate(response):
    auth = response.request.headers.get("Authorization")

    if auth is None:
        response.set_status(401)
        response.write('{"status":"error","message":"Missing Authorization header"}')
        response.flush()

    if auth.startswith("Basic"):
        base64enc = auth[6:]
        credentials = base64.b64decode(base64enc).decode()
        hyphen_index = credentials.find("-")
        colon_index = credentials.find(":")

        if colon_index is -1 or hyphen_index is -1:
            response.set_status(401)
            response.write('{"status":"error","message":"Invalid Authorization header"}')
            response.flush()
        else:
            owner = credentials[:hyphen_index]
            plugin_id = credentials[hyphen_index + 1: colon_index]
            token = credentials[colon_index + 1:]

            plugin_service = PluginService()

            if plugin_service.validate_plugin(owner, plugin_id, token):
                return {
                    "valid": True,
                    "owner": owner
                }
            else:
                response.set_status(403)
                response.write('{"status":"error","message":"Do not have authorization to R/W survey"}')
                response.flush()

    else:
        response.set_status(401)
        response.write('{"status":"error","message":"Invalid Authorization header - no basic"}')
        response.flush()

    return {"valid": False}


class ParticipantHandler(RequestHandler):

    # GET /participants?survey_id=<SURVEY_ID> <- Should return participant for survey_id
    def get(self):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_master_id = self.get_argument("survey_id")
            survey_service = SurveyService()

            survey_id = survey_master_id[0:survey_master_id.find("_")]
            survey_instance_id = survey_master_id[survey_master_id.find("_") + 1:]
            survey = survey_service.get_survey(survey_id, survey_instance_id)

            if survey is None:
                response = {
                    "status": "error",
                    "message": "Survey ID is invalid"
                }

                self.set_status(400)
                self.write(json.dumps(response))
                self.flush()
            else:
                if survey.owner == auth_response["owner"]:
                    response = {
                        "status": "success",
                        "participant": survey.participant_payload
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
