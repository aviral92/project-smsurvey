import json
import base64

from tornado.web import RequestHandler
from tornado.escape import json_decode

from smsurvey.core.model.survey.survey_state_machine import SurveyStatus
from smsurvey.core.model.survey.survey_state_machine import SurveyState
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.core.services.question_service import QuestionService
from smsurvey.core.services.response_service import ResponseService
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


class AllSurveysHandler(RequestHandler):
    # GET /surveys <- Should return all ongoing surveys that my plugin has access to
    def get(self):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_state_service = SurveyStateService()
            survey_ids = survey_state_service.get_by_owner(auth_response["owner"])
            self.set_status(200)
            self.write('{"status":"success","ids":' + json.dumps(list(set(survey_ids))) + '}')

    def data_received(self, chunk):
        pass


class LatestQuestionHandler(RequestHandler):
    # GET /surveys/[survey-id]/latest <- Should return me the text of the latest question in this survey,
    #  as well as the question-id. If no questions left, return an error message indicating as such
    def get(self, survey_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_state_service = SurveyStateService()
            survey_state = survey_state_service.get_by_instance_and_status(survey_id,
                                                                           SurveyStatus.AWAITING_USER_RESPONSE)

            if survey_state is None:
                self.set_status(410)
                self.write('{"status":"error","message":"No response was expected for this survey"}')
                self.finish()
            else:
                if survey_state.owner == auth_response['owner']:
                    question_service = QuestionService()
                    question = question_service.get(survey_state.next_question)

                    if question is not None:
                        self.set_status(200)
                        self.write('{"status":"success","question_id":"' + survey_state.next_question
                                   + '","question_text":"' + question.question_text + '","survey_end":"'
                                   + str(question.final) + '"}')
                        self.flush()
                    else:
                        self.set_status(410)
                        self.write('{"status":"error","message":"No more questions in this survey"}')
                        self.flush()
                else:
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner has not registered plugin"}')
                    self.flush()

    # POST /surveys/[survey-id]/latest <- posts a response to the latest survey question.
    #  Returns whether the response was accepted. If yes, latest increments to next question,
    #  if no, latest remains (and a message is returned for the plugin to optionally relay onto the participant).
    def post(self, survey_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            data = json_decode(self.request.body)

            if 'response' in data:
                response = data['response']
            else:
                self.set_status(400)
                self.write('{"status":"error","message":"Missing response parameter"}')
                self.flush()
                return

            survey_state_service = SurveyStateService()
            survey_state = survey_state_service.get_by_instance_and_status(survey_id, SurveyStatus.AWAITING_USER_RESPONSE)

            if survey_state is not None:
                if survey_state.owner == auth_response['owner']:
                    question_id = survey_state.next_question

                    question_service = QuestionService()
                    question = question_service.get(question_id)

                    if question is not None:
                        if question.final:
                            survey_state.survey_status = SurveyStatus.TERMINATED_COMPLETE
                            survey_state_service.update(survey_state)

                            self.set_status(200)
                            self.write('{"status":"success","response_accepted":"false","reason":"Survey has finished"}')
                            self.flush()
                        else:
                            survey_state.survey_status = SurveyStatus.PROCESSING_USER_RESPONSE
                            survey_state_service.update(survey_state)

                            new_questions = question.process(response)
                            if new_questions == 'INV_RESP':
                                survey_state.survey_status = SurveyStatus.AWAITING_USER_RESPONSE
                                survey_state_service.update(survey_state)

                                self.set_status(200)
                                self.write('{"status":"success","response_accepted":"False","reason":"Invalid Response","pass_along_message":"'
                                           + question.invalid_message + '"}')
                                self.flush()
                            else:
                                response_service = ResponseService()
                                variable_name = question.variable_name
                                survey = survey_id[:survey_id.find('_')]
                                response_service.insert_response(survey, survey_id, variable_name, response)

                                if new_questions is not None:
                                    for new_question in new_questions:
                                        state = SurveyState.new_state_object(survey_id, auth_response['owner'],
                                                                             new_question[0], new_question[1])
                                        state.survey_status = SurveyStatus.CREATED_MID
                                        survey_state_service.insert(state)

                                survey_state.survey_status = SurveyStatus.TERMINATED_COMPLETE
                                survey_state_service.update(survey_state)

                                new_survey_state = survey_state_service.get_by_instance_and_status(survey_id,
                                                                                                   SurveyStatus.CREATED_MID)

                                new_survey_state.survey_status = SurveyStatus.AWAITING_USER_RESPONSE
                                survey_state_service.update(new_survey_state)

                                self.set_status(200)
                                self.write('{"status":"success","response_accepted":"True"}')
                                self.flush()

                    else:
                        self.set_status(410, "No response was expected for this survey")
                        self.write('{"status":"error","message":"No response was expected for this survey"}')
                        self.finish()
                else:
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner does not have authorization to modify survey"}')
                    self.flush()
            else:
                self.set_status(410)
                self.write('{"status":"error","message":"No response was expected for this survey"}')
                self.finish()

    def data_received(self, chunk):
        pass


class AQuestionHandler(RequestHandler):
    # GET /surveys/[survey-id]/[question-id] <- Should return me the question text for that question id,
    #  plus any response if that response has been provided
    def get(self, survey_id, question_id):
        auth_response = authenticate(self)

        if auth_response['valid']:
            survey_state_service = SurveyStateService()
            survey_state = survey_state_service.get(survey_id, question_id)

            if survey_state is None:
                self.set_status(404)
                self.write('{"status":"error","message":"Question or survey does not exist"}')
                self.finish()
            else:
                question_service = QuestionService()
                question = question_service.get(survey_state.next_question)

                if question is None:
                    self.set_status(404)
                    self.write('{"status":"error","message":"Question does not exist"}')
                    self.finish()
                else:
                    q_text = question.question_text

                    if survey_state.survey_status == SurveyStatus.TERMINATED_COMPLETE:
                        response_service = ResponseService(c)
                        survey = survey_id[:survey_id.find('_')]
                        response_set = response_service.get_response_set(survey, survey_id)
                        response = response_set.get_response(question.variable_name)

                        self.set_status(200)
                        self.write('{"status":"success","question_text":"' + q_text
                                   + '","responded":"True","response:":"' + response + '"')
                        self.finish()
                    else:
                        self.set_status(200)
                        self.write('{"status":"success","question_text":"' + q_text + '","responded":"False"')
                        self.finish()

    def data_received(self, chunk):
        pass


class ASurveyHandler(RequestHandler):
    # GET/surveys/[survey-id] <- Should return state of this current survey, given I have authorization
    def get(self, survey_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            survey_state_service = SurveyStateService()
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
                    elif survey_state.survey_status == SurveyStatus.TERMINATED_COMPLETE:
                        self.set_status(200)
                        self.write('{"status":"success","survey_status":"COMPLETE"}')
                        self.flush()
                    else:
                        self.set_status(200)
                        self.write('{"status":"success","survey_status":"IN PROGRESS"}')
                        self.flush()

                else:
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner does not have authorization to see this survey"}')
                    self.flush()

    # POST /surveys/[survey-id] <- Should allow me to modify the state of the survey (start the survey)
    def post(self, survey_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            data = json_decode(self.request.body)

            if 'action' in data:
                action = data['action'].lower()
            else:
                self.set_status(400)
                self.write('{"status":"error","message":"Missing action parameter"}')
                self.flush()
                return

            if action == 'start':
                survey_state_service = SurveyStateService()
                survey_state = survey_state_service.get_by_instance_and_status(survey_id, SurveyStatus.CREATED_START)

                if survey_state is not None:
                    if survey_state.owner == auth_response['owner']:
                        survey_state.survey_status = SurveyStatus.AWAITING_USER_RESPONSE
                        survey_state_service.update(survey_state)
                        self.set_status(200)
                        self.write('{"status":"success","survey_status":"STARTED"}')
                        self.flush()
                    else:
                        self.set_status(403)
                        self.write('{"status":"error","message":"Owner does not have authorization to start survey"}')
                        self.flush()
                else:
                    self.set_status(410)
                    self.write('{"status":"error","message":"Survey already started, or does not exist"}')
                    self.flush()
            else:
                self.set_status(400)
                self.write('{"status":"error","message":"Invalid action parameter"}')
                self.flush()

    def data_received(self, chunk):
        pass
