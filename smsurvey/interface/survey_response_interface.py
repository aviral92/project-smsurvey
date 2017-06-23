from tornado import process
from tornado.web import RequestHandler
from tornado.web import Application

from smsurvey import config
from smsurvey.core.model.survey.survey_state_machine import SurveyStatus
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.core.services.question_service import QuestionService


def initiate_interface():
    process_id = process.fork_processes(config.response_interface_processes, max_restarts=0)

    instance = Application([
        (r"/surveys", SurveyResponseHandler)
    ])

    port = config.survey_response_interface_port_begin + process_id
    instance.listen(port)
    print("Survey Response Interface Handler listening on " + port)


class SurveyResponseHandler(RequestHandler):
    def post(self):
        participant = self.get_argument("participant")
        survey_id = self.get_argument("survey_id")
        survey_response = self.get_argument("survey_response")
        plugin_owner = self.get_argument("owner")
        plugin_key = self.get_argument("key")
        plugin_secret_token = self.get_argument("secret_token")

        plugin_service = PluginService(config.dynamo_url, config.plugin_backend_name)
        if plugin_service.validate_plugin(plugin_owner, plugin_key, plugin_secret_token):
            survey_service = SurveyService(config.dynamo_url, config.survey_backend_name)
            survey = survey_service.get_survey(survey_id, participant)
            if survey is not None:
                survey_state_service = SurveyStateService(config.dynamo_url, config.survey_state_backend_name)
                survey_state = survey_state_service.get_by_instance_and_status(survey.survey_instance_id,
                                                                               SurveyStatus.AWAITING_USER_RESPONSE)
                if survey_state is not None:
                    survey_state.survey_status = SurveyStatus.PROCESSING_USER_RESPONSE
                    survey_state_service.update(survey_state.event_id, survey_state)
                    question_service = QuestionService(config.dynamo_url, config.question_backend_name)
                    question = question_service.get(survey_state.next_question)

                    if question is not None:
                        new_survey_state = question.process(survey_response)
                        survey_state_service.insert(new_survey_state)
                        survey_state.survey_status = SurveyStatus.TERMINATED_COMPLETE
                        survey_state_service.update(survey_state.event_id, survey_state)

                        new_question = question_service.get(new_survey_state.next_question)
                        message = new_question.question_text
                        end = new_question.is_final_question()
                        self.set_status(200)
                        self.write('{"status":"Processed successfully","is_end":"' + end + '","message":' + message
                                   + '}')
                        self.finish()
                    else:
                        self.set_status(410, "No response was expected from this participant")
                        self.finish()
                else:
                    self.set_status(410, "No response expected from this participant")
                    self.finish()
            else:
                self.set_status(410, "This participant is not in any active surveys")
                self.finish()
        else:
            self.set_status(401, "Invalid credentials")
            self.finish()

    def data_received(self, chunk):
        pass
