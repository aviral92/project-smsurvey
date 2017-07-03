import json
import base64

from tornado.web import RequestHandler
from tornado.escape import json_decode

from smsurvey import config
from smsurvey.core.model.survey.survey_state_machine import SurveyStatus
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.core.services.question_service import QuestionService
from smsurvey.core.services.response_service import ResponseService


def authenticate(response):
    auth = response.request.headers.get("Authorization")

    if auth is None:
        response.set_status(403)
        response.write('{"status":"error","message":"Missing Authorization header"}')
        response.flush()

    if auth.startswith("Basic"):
        base64enc = auth[6:]
        credentials = base64.b64decode(base64enc).decode()
        hyphen_index = credentials.find("-")
        colon_index = credentials.find(":")

        if colon_index is -1 or hyphen_index is -1:
            response.set_status(403)
            response.write('{"status":"error","message":"Invalid Authorization header"}')
            response.flush()
        else:
            owner = credentials[:hyphen_index]
            plugin_id = credentials[hyphen_index + 1: colon_index]
            token = credentials[colon_index + 1:]

            plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)

            if plugin_service.validate_plugin(owner, plugin_id, token):
                return {
                    "valid": True,
                    "owner": owner
                }

    else:
        response.set_status(403)
        response.write('{"status":"error","message":"Invalid Authorization header - no basic"}')
        response.flush()

    return {"valid": False}


class AllSurveysHandler(RequestHandler):
    # GET /surveys <- Should return all ongoing surveys that my plugin has access to
    def get(self):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_ids = survey_state_service.get_by_owner(auth_response["owner"])
            self.set_status(200)
            self.write('{"status":"success","ids":' + json.dumps(survey_ids) + '}')

    def data_received(self, chunk):
        pass


class LatestQuestionHandler(RequestHandler):
    # GET /surveys/[survey-id]/latest <- Should return me the text of the latest question in this survey,
    #  as well as the question-id. If no questions left, return an error message indicating as such
    def get(self, survey_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_state = survey_state_service.get_by_instance_and_status(survey_id,
                                                                           SurveyStatus.AWAITING_USER_RESPONSE)

            if survey_state is None:
                self.set_status(410)
                self.write('{"status":"error","message":"No response was expected for this survey"}')
                self.finish()
            else:
                if survey_state.owner == auth_response['owner']:
                    question_service = QuestionService(config.dynamo_url, config.question_backend_name)
                    question = question_service.get(survey_state.next_question)

                    if question is not None:
                        self.set_status(200)
                        self.write('{"status":"success","question_text":"' + question.question_text + '"}')
                        self.flush()
                    else:
                        self.set_status(410)
                        self.write('{"status":"error","message":"No more questions in this survey"}')
                        self.flush()
                else:
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner does not have authorization to modify this survey"}')
                    self.flush()

    # POST /surveys/[survey-id]/latest <- posts a response to the latest survey question.
    #  Returns whether the response was accepted. If yes, latest increments to next question,
    #  if no, latest remains (and a message is returned for the plugin to optionally relay onto the participant).
    def post(self, survey_id):
        print("post - Not implemented. survey_id = " + survey_id)

    def data_received(self, chunk):
        pass


class AQuestionHandler(RequestHandler):
    # GET /surveys/[survey-id]/[question-id] <- Should return me the question text for that question id,
    #  plus any response if that response has been provided
    def get(self, survey_id, question_id):
        print("get - Not implemented. survey_id = " + survey_id + ". question_id = " + question_id)

    def data_received(self, chunk):
        pass


class ASurveyHandler(RequestHandler):
    # GET/surveys/[survey-id] <- Should return state of this current survey, given I have authorization
    def get(self, survey_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_state = survey_state_service.get_by_instance(survey_id)

            if survey_state is None:
                self.set_status(404)
                self.write('{"status":"error","message":"Survey does not exist"}')
                self.finish()
            else:
                if survey_state.owner == auth_response["owner"]:
                    if survey_state.survey_status == SurveyStatus.CREATED_START:
                        self.set_status(200)
                        self.write('{"status":"success","survey_status":"NOT STARTED"}')
                        self.flush()
                    elif survey_state.survey_status == SurveyStatus.AWAITING_USER_RESPONSE or \
                                    survey_state.survey_status == SurveyStatus.CREATED_MID or \
                                    survey_state.survey_status == SurveyStatus.PROCESSING_USER_RESPONSE:
                        self.set_status(200)
                        self.write('{"status":"success","survey_status":"IN PROGRESS"}')
                        self.flush()
                    else:
                        self.set_status(200)
                        self.write('{"status":"success","survey_status":"COMPLETE"}')
                        self.flush()
                else:
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner does not have authorization to see this survey"}')
                    self.flush()

    # POST /surveys/[survey-id] <- Should allow me to modify the state of the survey (start the survey)
    def post(self, survey_id):
        print("post - Not implemented. survey_id = " + survey_id)

    def data_received(self, chunk):
        pass


class SurveyHandler(RequestHandler):
    def post(self, survey_id):
        data = json_decode(self.request.body)

        if survey_id == "":
            self.set_status(400)
            self.write('{"status":"error","message":"Missing survey_id in url"}')
            self.flush()
            return

        if 'response' in data:
            response = data['response']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing response parameter"}')
            return

        if 'owner' in data:
            owner = data['owner']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing owner parameter"}')
            return

        if 'plugin_id' in data:
            plugin_id = data['plugin_id']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing plugin_id parameter"}')
            return

        if 'token' in data:
            token = data['token']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing token parameter"}')
            return

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(owner, plugin_id, token):

            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_state = survey_state_service.get_by_instance_and_status(survey_id,
                                                                           SurveyStatus.AWAITING_USER_RESPONSE)

            if survey_state is not None:
                survey_state.survey_status = SurveyStatus.PROCESSING_USER_RESPONSE
                survey_state_service.update(survey_state)

                question_service = QuestionService(config.dynamo_url, config.question_backend_name)
                question = question_service.get(survey_state.next_question)

                new_survey_state = None

                if question is not None:
                    response_service = ResponseService(config.dynamo_url, config.response_backend_name)
                    variable_name = question.variable_name
                    # TODO: survey id not yet implemented, as in MVP only one survey
                    response_service.insert_response("1", survey_id, variable_name, response)
                    new_states = question.process(response)

                    if new_states is not None:
                        for state in new_states:
                            state.survey_status = SurveyStatus.CREATED_MID
                            state.owner = owner
                            survey_state_service.insert(state)

                    if new_survey_state is None:
                        new_survey_state = survey_state_service.get_by_instance_and_status(
                            survey_state.survey_instance_id, SurveyStatus.CREATED_MID)

                    survey_state.survey_status = SurveyStatus.TERMINATED_COMPLETE
                    survey_state_service.update(survey_state)

                    if new_survey_state is None:
                        self.set_status(410)
                        self.write('{"status":"error","message":"Survey has completed"}')
                        self.flush()
                        return

                    new_survey_state.survey_status = SurveyStatus.AWAITING_USER_RESPONSE
                    survey_state_service.update(new_survey_state)
                    new_question = question_service.get(new_survey_state.next_question)
                    message = new_question.question_text
                    end = new_question.final

                    self.set_status(200)
                    self.write('{"status":"success","is_end":"' + str(end) + '","message":"' + message + '"}')
                    self.flush()
                else:
                    self.set_status(410, "No response was expected for this survey")
                    self.write('{"status":"error","message":"No response was expected for this survey"}')
                    self.finish()
            else:
                self.set_status(410, "No response expected for this survey")
                self.write('{"status":"error","message":"No response was expected for this survey"}')
                self.flush()
        else:
            self.set_status(403, "Owner does not have ability to modify this survey")
            self.write('{"status":"error","message":"Owner does not have authorization to modify this survey"}')
            self.flush()

    def data_received(self, chunk):
        pass


class SurveysHandler(RequestHandler):
    def post(self):
        data = json_decode(self.request.body)

        if "status" in data:
            status = data["status"]
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing status parameter"}')
            return

        if "owner" in data:
            owner = data["owner"]
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing owner parameter"}')
            return

        if "plugin_id" in data:
            plugin_id = data["plugin_id"]
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing plugin_id parameter"}')
            return

        if "token" in data:
            token = data["token"]
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing token parameter"}')
            return

        if status != "new":
            self.set_status(400, "Only supported status currently is 'new'")
            self.write('{"status":"error","message":"Only supported status currently is new"}')
            return

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(owner, plugin_id, token):
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_ids = survey_state_service.get_by_owner(owner, SurveyStatus.CREATED_START)
            self.set_status(200)
            self.write('{"status":"success","ids":' + json.dumps(survey_ids) + '}')
        else:
            self.set_status(403)
            self.write('{"status":"error","message":"Unauthorized"}')

    def data_received(self, chunk):
        pass


class NewSurveyHandler(RequestHandler):
    def post(self, survey_id):
        data = json_decode(self.request.body)

        if 'owner' in data:
            owner = data['owner']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing owner parameter"}')
            return

        if 'plugin_id' in data:
            plugin_id = data['plugin_id']
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing plugin_id parameter"}')
            return

        if "token" in data:
            token = data["token"]
        else:
            self.set_status(400)
            self.write('{"status":"error","message":"Missing token parameter"}')
            return

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(owner, plugin_id, token):
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_state = survey_state_service.get(survey_id, "1_1")

            if survey_state is not None:
                if survey_state.owner == owner:
                    if survey_state.survey_status == SurveyStatus.CREATED_START:
                        survey_state.survey_status = SurveyStatus.AWAITING_USER_RESPONSE
                        survey_state_service.update(survey_state)
                        question_service = QuestionService(config.dynamo_url, config.question_backend_name)
                        question = question_service.get(survey_state.next_question)
                        message = question.question_text
                        end = question.final

                        self.set_status(200)
                        self.write('"status":"success","is_end":' + str(end) + '","message":"' + message + '"')
                    else:
                        self.set_status(410, "Survey already started")
                        self.write('{"status":"error","message":"Survey already started"}')
                        self.flush()
                else:
                    self.set_status(403, "Owner does not have authorization to retrieve this survey")
                    self.write(
                        '{"status":"error","message":"Owner does not have authorization to retrieve this survey"}')
                    self.flush()
            else:
                self.set_status(410, "No survey matching this ID")
                self.write('{"status":"error","message":"No survey matching this ID"}')
                self.flush()

    def data_received(self, chunk):
        pass
