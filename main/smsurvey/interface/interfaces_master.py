
from tornado import process
from tornado.web import Application
from tornado.web import RequestHandler

from tornado.ioloop import IOLoop

from smsurvey import config
from smsurvey.interface.survey_interface import AllInstancesHandler
from smsurvey.interface.survey_interface import LatestQuestionHandler
from smsurvey.interface.survey_interface import AQuestionHandler
from smsurvey.interface.survey_interface import AnInstanceHandler
from smsurvey.interface.participant_interface import ParticipantHandler


def initiate_interface():
    process_id = process.fork_processes(config.response_interface_processes, max_restarts=0)

    instance = Application([

        (r"/instances", AllInstancesHandler),
        (r"/instances/(\d*)/latest", LatestQuestionHandler),
        (r"/instances/(\d*)/(\d*_*\d*)", AQuestionHandler),
        (r"/instances/(\d*)", AnInstanceHandler),
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
