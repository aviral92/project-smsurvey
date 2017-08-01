import json
import base64

from tornado.web import RequestHandler
from tornado.escape import json_decode

from smsurvey.core.model.survey.state import Status
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.state_service import StateService
from smsurvey.core.services.question_service import QuestionService
from smsurvey.core.services.response_service import ResponseService
from smsurvey.core.services.plugin_service import PluginService


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
        at_index = credentials.find("@")

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

            plugin_service = PluginService()

            if plugin_service.validate_plugin(plugin_id, owner_name, owner_domain, token):
                return {
                    "valid": True,
                    "owner_name": owner_name,
                    "owner_domain": owner_domain
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


class AllInstancesHandler(RequestHandler):
    # GET /instances <- Should return all ongoing instances that my plugin has access to
    def get(self):
        auth_response = authenticate(self)

        survey_id = self.get_argument("survey_id", None)
        status = self.get_argument("status", None)

        if status is not None:
            if status == "not_started":
                status = Status.CREATED_START
            else:
                self.set_status(400)
                self.write('{"status":"error","message":"Invalid start parameter - try not_started"}')
                self.flush()
                return

        if auth_response["valid"]:
            instance_service = InstanceService()
            instance_ids = instance_service.get_by_owner(auth_response["owner_name"], auth_response["owner_domain"],
                                                         survey_id, status)
            self.set_status(200)
            self.write('{"status":"success","ids":' + json.dumps(instance_ids) + '}')

    def data_received(self, chunk):
        pass


class LatestQuestionHandler(RequestHandler):
    # GET /instances/[instance-id]/latest <- Should return me the text of the latest question in this survey,
    #  as well as the question-id. If no questions left, return an error message indicating as such
    def get(self, instance_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            state_service = StateService()
            state = state_service.get_next_state_in_instance(instance_id, Status.AWAITING_USER_RESPONSE)

            if state is None:
                self.set_status(410)
                self.write('{"status":"error","message":"No response was expected for this survey"}')
                self.finish()
            else:
                owner = InstanceService().get_owner(instance_id)
                if owner.name == auth_response['owner_name'] and owner.domain == auth_response["owner_domain"]:
                    question_service = QuestionService()
                    question = question_service.get(state.question_id)

                    if question is not None:
                        self.set_status(200)
                        self.write('{"status":"success","question_id":"' + state.question_id
                                   + '","question_text":"' + question.question_text + '","survey_end":"'
                                   + str(question.final) + '"}')
                        self.flush()
                    else:
                        print('{"status":"error","message":"No more questions in this survey"}')
                        self.set_status(410)
                        self.write('{"status":"error","message":"No more questions in this survey"}')
                        self.flush()
                else:
                    print('{"status":"error","message":"Owner has not registered plugin"}')
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner has not registered plugin"}')
                    self.flush()

    # POST /instances/[instance-id]/latest <- posts a response to the latest instance question.
    #  Returns whether the response was accepted. If yes, latest increments to next question,
    #  if no, latest remains (and a message is returned for the plugin to optionally relay onto the participant).
    def post(self, instance_id):
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

            state_service = StateService()
            state = state_service.get_next_state_in_instance(instance_id, Status.AWAITING_USER_RESPONSE)

            if state is not None:
                owner = InstanceService().get_owner(instance_id)
                if owner.name == auth_response['owner_name'] and owner.domain == auth_response['owner_domain']:
                    question_id = state.question_id

                    question_service = QuestionService()
                    question = question_service.get(question_id)

                    if question is not None:
                        if question.final:
                            state.status = Status.TERMINATED_COMPLETE
                            state_service.update_state(state)

                            self.set_status(200)
                            self.write('{"status":"success","response_accepted":"False","reason":"Survey has finished"}')
                            self.flush()
                        else:
                            state.status = Status.PROCESSING_USER_RESPONSE
                            state_service.update_state(state)

                            new_questions = question.process(response)
                            if new_questions == 'INV_RESP':
                                state.status = Status.AWAITING_USER_RESPONSE
                                state_service.update_state(state)

                                self.set_status(200)
                                self.write('{"status":"success","response_accepted":"False","reason":"Invalid Response","pass_along_message":"'
                                           + question.invalid_message + '"}')
                                self.flush()
                            else:
                                response_service = ResponseService()
                                variable_name = question.variable_name
                                instance_service = InstanceService()
                                survey_id = instance_service.get_survey_id(instance_id)
                                response_service.insert_response(survey_id, instance_id, variable_name, response)

                                if new_questions is not None:
                                    for new_question in new_questions:
                                        state_service.create_state(state.instance_id, new_question[0],
                                                                   Status.CREATED_MID, new_question[1])

                                state.status = Status.TERMINATED_COMPLETE
                                state_service.update_state(state)

                                new_state = state_service.get_next_state_in_instance(instance_id, Status.CREATED_MID)

                                new_state.status = Status.AWAITING_USER_RESPONSE
                                state_service.update_state(new_state)

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
    # GET /instances/[instance-id]/[question-id] <- Should return me the question text for that question id,
    #  plus any response if that response has been provided
    def get(self, instance_id, question_id):
        auth_response = authenticate(self)

        if auth_response['valid']:
            state_service = StateService()
            state = state_service.get_state_by_instance_and_question(instance_id, question_id)

            if state is None:
                self.set_status(404)
                self.write('{"status":"error","message":"Question or survey does not exist"}')
                self.finish()
            else:
                question_service = QuestionService()
                question = question_service.get(state.question_id)

                if question is None:
                    self.set_status(404)
                    self.write('{"status":"error","message":"Question does not exist"}')
                    self.finish()
                else:
                    q_text = question.question_text

                    if state.status == Status.TERMINATED_COMPLETE:
                        response_service = ResponseService()
                        survey_id = InstanceService().get_survey_id(instance_id)
                        response_set = response_service.get_response_set(survey_id, instance_id)
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


class AnInstanceHandler(RequestHandler):
    # GET/instances/[instance-id] <- Should return state of this current survey, given I have authorization
    def get(self, instance_id):
        auth_response = authenticate(self)

        if auth_response["valid"]:
            state_service = StateService()
            state = state_service.get_next_state_in_instance(instance_id)

            if state is None:
                self.set_status(404)
                self.write('{"status":"error","message":"Survey does not exist"}')
                self.finish()
            else:
                owner = InstanceService().get_owner(instance_id)
                if owner.domain == auth_response["owner_domain"] and owner.name == auth_response["owner_name"]:
                    if state.status == Status.CREATED_START:
                        self.set_status(200)
                        self.write('{"status":"success","status":"NOT STARTED"}')
                        self.flush()
                    elif state.status == Status.TERMINATED_COMPLETE:
                        self.set_status(200)
                        self.write('{"status":"success","status":"COMPLETE"}')
                        self.flush()
                    else:
                        self.set_status(200)
                        self.write('{"status":"success","status":"IN PROGRESS"}')
                        self.flush()

                else:
                    self.set_status(403)
                    self.write('{"status":"error","message":"Owner does not have authorization to see this survey"}')
                    self.flush()

    # POST /instances/[instance-id] <- Should allow me to modify the state of the survey (start the survey)
    def post(self, instance_id):
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
                state_service = StateService()
                state = state_service.get_next_state_in_instance(instance_id, Status.CREATED_START)

                if state is not None:
                    owner = InstanceService().get_owner(instance_id)
                    if owner.domain == auth_response["owner_domain"] and owner.name == auth_response["owner_name"]:
                        state.status = Status.AWAITING_USER_RESPONSE
                        state_service.update_state(state)
                        self.set_status(200)
                        self.write('{"status":"success","status":"STARTED"}')
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
