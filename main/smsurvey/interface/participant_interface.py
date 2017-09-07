import base64
import json

from tornado.web import RequestHandler

from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.participant_service import ParticipantService

from smsurvey.core.security.permissions import Permissions, authenticate


class ParticipantHandler(RequestHandler):

    # GET /participants?survey_id=<SURVEY_ID>&instance_id=<INSTANCE_ID> <- Should return participant for instance_id
    def get(self):
        auth_response = authenticate(self, [Permissions.READ_PARTICIPANT])

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
                if str(survey.owner_id) == auth_response["owner_id"]:

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
