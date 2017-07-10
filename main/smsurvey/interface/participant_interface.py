import json

from tornado.web import RequestHandler

from smsurvey.interface.interfaces_master import authenticate
from smsurvey.core.services.survey_service import SurveyService


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
