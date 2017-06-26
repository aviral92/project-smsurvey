import json

from tornado.web import RequestHandler

from smsurvey import config
from smsurvey.core.model.survey.survey_state_machine import SurveyStatus
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.core.services.question_service import QuestionService


class SurveyHandler(RequestHandler):

    def get(self, survey_id):
        owner = self.get_argument("owner")
        plugin_key = self.get_argument("key")
        plugin_secret_token = self.get_argument("secret_token")

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(owner, plugin_key, plugin_secret_token):
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_state = survey_state_service.get(survey_id)

            if survey_state is not None:
                if survey_state.owner == owner:
                    if survey_state.survey_status != SurveyStatus.CREATED_START:
                        question_service = QuestionService(config.dynamo_url, config.question_backend_name)
                        question = question_service.get(survey_state.next_question)
                        message = question.question_text
                        end = question.final

                        self.set_status(200)
                        self.write('"status":"success","is_end":' + end + '"message":"' + message + '"')
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

    def post(self, survey_id):
        participant = self.get_argument("participant")
        survey_response = self.get_argument("survey_response")
        plugin_owner = self.get_argument("owner")
        plugin_key = self.get_argument("key")
        plugin_secret_token = self.get_argument("secret_token")

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(plugin_owner, plugin_key, plugin_secret_token):
            survey_service = SurveyService(config.dynamo_url, config.survey_backend_name)
            survey = survey_service.get_survey(survey_id, participant)
            if survey is not None:
                if survey.owner == plugin_owner:
                    survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
                    survey_state = survey_state_service.get_by_instance_and_status(survey.survey_instance_id,
                                                                                   [SurveyStatus.AWAITING_USER_RESPONSE,
                                                                                    SurveyStatus.CREATED_START])
                    if survey_state is not None:
                        survey_state.survey_status = SurveyStatus.PROCESSING_USER_RESPONSE
                        survey_state_service.update(survey_state.event_id, survey_state)
                        question_service = QuestionService(config.dynamo_url, config.question_backend_name)
                        question = question_service.get(survey_state.next_question)

                        if question is not None:
                            new_survey_state = question.process(survey_response)
                            new_survey_state.survey_status = SurveyStatus.CREATED_MID
                            new_survey_state.owner = plugin_owner
                            survey_state_service.insert(new_survey_state)
                            survey_state.survey_status = SurveyStatus.TERMINATED_COMPLETE
                            survey_state_service.update(survey_state.event_id, survey_state)

                            new_question = question_service.get(new_survey_state.next_question)
                            message = new_question.question_text
                            end = new_question.is_final_question()
                            self.set_status(200)
                            self.write('{"status":"success","is_end":"' + end + '","message":"' + message
                                       + '"}')
                            self.finish()
                        else:
                            self.set_status(410, "No response was expected from this participant")
                            self.write('{"status":"error","message":"No response was expected from this participant"}')
                            self.finish()
                    else:
                        self.set_status(410, "No response expected from this participant")
                        self.write('{"status":"error","message":"No response expected from this participant"}')
                        self.finish()
                else:
                    self.set_status(403, "Owner does not have ability to modify this survey")
                    self.write('{"status":"error","message":"Owner does not have authorization to modify this survey"}')
            else:
                self.set_status(410, "This participant is not in any active surveys")
                self.write('{"status":"error","message":"This participant is not in any active surveys"}')
                self.finish()
        else:
            self.set_status(401, "Invalid credentials")
            self.write('{"status":"error","message":"Invalid credentials"}')
            self.finish()

    def data_received(self, chunk):
        pass


class SurveysHandler(RequestHandler):

    def post(self):
        #TODO: These need to be fixed
        status = self.get_body_argument("status")
        plugin_owner = self.get_argument("owner")
        plugin_key = self.get_argument("key")
        plugin_secret_token = self.get_argument("secret_token")


        if status != "new":
            self.set_status(400, "Only supported status currently is 'new'")
            self.write('{"status":"error","message":"Only supported status current is <new>"}')
            self.finish()
            return

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(plugin_owner, plugin_key, plugin_secret_token):
            survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
            survey_ids = survey_state_service.get_by_owner(plugin_owner, SurveyStatus.CREATED_START)
            self.set_status(200)
            self.write('{"status":"success","ids":' + json.dumps(survey_ids) + '}')
            self.finish()

    def data_received(self, chunk):
        pass
