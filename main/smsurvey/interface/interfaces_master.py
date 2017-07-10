import base64

from tornado import process
from tornado.web import Application
from tornado.web import RequestHandler

from tornado.ioloop import IOLoop

from smsurvey import config
from smsurvey.interface.services.plugin_service import PluginService
from smsurvey.interface.survey_interface import AllSurveysHandler
from smsurvey.interface.survey_interface import LatestQuestionHandler
from smsurvey.interface.survey_interface import AQuestionHandler
from smsurvey.interface.survey_interface import ASurveyHandler
from smsurvey.interface.participant_interface import ParticipantHandler


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


def initiate_interface():
    process_id = process.fork_processes(config.response_interface_processes, max_restarts=0)

    instance = Application([

        (r"/surveys", AllSurveysHandler),
        (r"/surveys/(\d*_*\d*)/latest", LatestQuestionHandler),
        (r"/surveys/(\d*_*\d*)/(\d*_*\d*)", AQuestionHandler),
        (r"/surveys/(\d*_*\d*)", ASurveyHandler),
        (r"/participants", ParticipantHandler),
        (r"/healthcheck", HealthCheckHandler)
    ])

    port = config.survey_response_interface_port_begin + process_id
    instance.listen(port)
    print("Survey Response Interface Handler listening on " + str(port))
    IOLoop.current().start()


class HealthCheckHandler(RequestHandler):

    def data_received(self, chunk):
        pass

    def get(self):
        self.set_status(200)
        self.write("Healthy")
        self.flush()
