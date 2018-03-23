import json
import pytz

from datetime import datetime

from tornado.escape import json_decode
from tornado.web import RequestHandler

from smsurvey.config import logger
from smsurvey.core.security.permissions import Permissions, authenticate
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.question_service import QuestionService
from smsurvey.core.services.response_service import ResponseService
from smsurvey.core.services.state_service import StateService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.model.status import Status
from smsurvey.interface.participantsdetails import LoadData
from smsurvey.interface.datamanagement import LoadData1

class AllInstancesHandler(RequestHandler):
    # GET /instances <- Should return all ongoing instances that my plugin has access to
    def get(self):
        logger.debug("Getting instances")
        auth_response = authenticate(self, [Permissions.READ_SURVEY])

        survey_id = self.get_argument("survey_id", None)
        status = self.get_argument("status", None)

        if auth_response["valid"]:

            owner_id = auth_response["owner_id"]

            if status is not None:
                instances = InstanceService.get_by_owner(owner_id, survey_id, Status.CREATED_START)
            else:
                instances = InstanceService.get_by_owner(owner_id, survey_id)

            instance_ids = [instance.id for instance in instances]

            self.set_status(200)

            response = {
                "status": "success",
                "ids": instance_ids
            }

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass


class LatestQuestionHandler(RequestHandler):
    # GET /instances/[instance-id]/latest <- Should return me the text of the latest question in this survey,
    #  as well as the question-id. If no questions left, return an error message indicating as such
    def get(self, instance_id):
        auth_response = authenticate(self, [Permissions.READ_QUESTION])

        if auth_response["valid"]:
            instance = InstanceService.get_instance(instance_id)
            state = StateService.get_next_state_in_instance(instance, Status.AWAITING_USER_RESPONSE)

            if state is None:
                self.set_status(410)
                response = {
                    "status": "error",
                    "message": "No response was expected for this survey"
                }
            else:
                survey = SurveyService.get_survey(instance.survey_id)
                if str(survey.owner_id) == auth_response['owner_id']:
                    question_service = QuestionService()
                    question = question_service.get(survey.protocol_id, state.question_number)

                    if question is not None:
                        self.set_status(200)

                        response = {
                            "status": "success",
                            "question_number": state.question_number,
                            "question_text": question.question_text,
                            "survey_end": question.final
                        }
                    else:
                        self.set_status(410)
                        response = {
                            "status": "error",
                            "message": "No more questions in this survey"
                        }
                else:
                    self.set_status(403)
                    response = {
                        "status": "error",
                        "message": "Owner has not registered plugin"
                    }

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()


    # POST /instances/[instance-id]/latest <- posts a response to the latest instance question.
    #  Returns whether the response was accepted. If yes, latest increments to next question,
    #  if no, latest remains (and a message is returned for the plugin to optionally relay onto the participant).
    def post(self, instance_id):
        auth_response = authenticate(self, [Permissions.WRITE_RESPONSE])
        if auth_response["valid"]:
            data = json_decode(self.request.body)
            if 'response' in data:
                response = data['response']
                contact = data['contact']
            else:
                self.set_status(400)
                self.write('{"status":"error","message":"Missing response parameter"}')
                return
            
            instance = InstanceService.get_instance(instance_id)
            if instance is None:
                self.set_status(410)
                self.write('{"status":"error","message":"No response was expected for this survey"}')
                self.finish()
                return

            instance_id = instance.id  # Ensure that id is of right type
            state = StateService.get_next_state_in_instance(instance, Status.AWAITING_USER_RESPONSE)
            if state is not None and state.status is not Status.NO_RESPONSE_REQUIRED:
                survey = SurveyService.get_survey(instance.survey_id)
                if str(survey.owner_id) == auth_response["owner_id"]:
                    question_number = state.question_number
                    question_service = QuestionService()
                    question = question_service.get(survey.protocol_id, question_number)
                    now = datetime.now(tz=pytz.utc)
                    now_csv_entry = str(datetime.now(tz=pytz.utc))
                    loaddata = LoadData()
                    participant_id = loaddata.sendparticpantid(contact)
                    loaddata_response = LoadData1()
                    #loaddata_response.concatresponse(participant_id,question_number,response, now_csv_entry[:10],now_csv_entry[11:16])
                    if question is not None:

                        if question.final:
                            state.status = Status.TERMINATED_COMPLETE.value
                            StateService.update_state(state)

                            self.set_status(200)
                            self.write('{"status":"success","response_accepted":"False","reason":"Survey has finished"}')
                            self.flush()
                        elif state.timeout.replace(tzinfo=pytz.utc) < now:
                            state.status = Status.TERMINATED_TIMEOUT.value
                            state.save()
                            self.set_status(200)
                            self.write(
                                '{"status":"success","response_accepted":"False","reason":"Survey has timed out"}')
                        else:
                            state.status = Status.PROCESSING_USER_RESPONSE.value
                            StateService.update_state(state)
                            loaddata_response.concatresponse(participant_id,question_number,response, now_csv_entry[:10])
                            new_questions = question.process(response)
                            if new_questions == 'INV_RESP':
                                state.status = Status.AWAITING_USER_RESPONSE.value
                                StateService.update_state(state)

                                self.set_status(200)
                                self.write('{"status":"success","response_accepted":"False","reason":"Invalid Response","pass_along_message":"'
                                           + question.invalid_message + '"}')
                                self.flush()
                            else:
                                response_service = ResponseService()
                                variable_name = question.variable_name
                                survey_id = instance.survey_id
                                response_service.insert_response(survey_id, instance_id, variable_name, response)

                                if new_questions is not None:
                                    for new_question in new_questions:
                                        #print("Is this the final question", isFinal)
                                        #if not new_question.final:
                                        if not question.final:
                                            status = Status.CREATED_MID
                                        else:
                                            status = Status.NO_RESPONSE_REQUIRED

                                        StateService.create_state(instance_id, new_question[0][1], status,
                                                                  state.timeout, new_question[1])

                                state.status = Status.TERMINATED_COMPLETE.value
                                StateService.update_state(state)

                                new_state = StateService.get_next_state_in_instance(instance, Status.CREATED_MID)

                                new_state.status = Status.AWAITING_USER_RESPONSE.value
                                StateService.update_state(new_state)

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
    # GET /instances/[instance-id]/[question-number] <- Should return me the question text for that question id,
    #  plus any response if that response has been provided
    def get(self, instance_id, question_number):
        auth_response = authenticate(self, [Permissions.READ_QUESTION])

        if auth_response['valid']:
            instance = InstanceService.get_instance(instance_id)
            instance_id = instance.id
            state = StateService.get_state_by_instance_and_question(instance, question_number)

            if state is None:
                self.set_status(404)
                self.write('{"status":"error","message":"Question or survey does not exist"}')
                self.finish()
            else:
                survey = SurveyService.get_survey(instance.survey_id)
                question_service = QuestionService()
                question = question_service.get(survey.protocol_id, state.question_number)

                if question is None:
                    self.set_status(404)
                    self.write('{"status":"error","message":"Question does not exist"}')
                    self.finish()
                else:
                    q_text = question.question_text

                    if state.status == Status.TERMINATED_COMPLETE:
                        response_service = ResponseService()
                        survey_id = instance.survey_id
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
        auth_response = authenticate(self, [Permissions.READ_QUESTION])

        if auth_response["valid"]:
            instance = InstanceService.get_instance(instance_id)
            state = StateService.get_next_state_in_instance(instance)

            if state is None:
                self.set_status(404)
                self.write('{"status":"error","message":"Survey does not exist"}')
                self.finish()
            else:
                survey = SurveyService.get_survey(instance.survey_id)
                if str(survey.owner_id) == auth_response["owner_id"]:
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
        auth_response = authenticate(self, [Permissions.WRITE_SURVEY])

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
                instance = InstanceService.get_instance(instance_id)
                state = StateService.get_next_state_in_instance(instance, Status.CREATED_START)

                if state is not None:
                    survey = SurveyService.get_survey(instance.survey_id)
                    if str(survey.owner_id) == auth_response["owner_id"]:
                        state.status = Status.AWAITING_USER_RESPONSE.value
                        StateService.update_state(state)
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
