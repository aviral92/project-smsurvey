import json

from tornado.web import RequestHandler
from tornado.escape import json_decode

from smsurvey import config
from smsurvey.core.model.survey.survey_state_machine import SurveyStatus
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.core.services.question_service import QuestionService


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
        print(survey_id)
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
            survey_state = survey_state_service.get(survey_id, survey_id + "_" + "1_1")

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
                    self.write('{"status":"error","message":"No survey matching this ID"}')
                    self.flush()
            else:
                self.set_status(410, "No survey matching this ID")
                self.write('{"status":"error","message":"No survey matching this ID"}')
                self.flush()

    def data_received(self, chunk):
        pass
