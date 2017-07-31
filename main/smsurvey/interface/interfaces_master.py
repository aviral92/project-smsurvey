from tornado.web import Application, RequestHandler

from smsurvey.interface.survey_interface import AllInstancesHandler
from smsurvey.interface.survey_interface import LatestQuestionHandler
from smsurvey.interface.survey_interface import AQuestionHandler
from smsurvey.interface.survey_interface import AnInstanceHandler
from smsurvey.interface.participant_interface import ParticipantHandler


class HealthCheckHandler(RequestHandler):

    def data_received(self, chunk):
        pass

    def get(self):
        self.set_status(200)
        self.write("Healthy")
        self.flush()


def start_interface(port):
    instance = Application([

        (r"/instances", AllInstancesHandler),
        (r"/instances/(\d*)/latest", LatestQuestionHandler),
        (r"/instances/(\d*)/(\d*_*\d*)", AQuestionHandler),
        (r"/instances/(\d*)", AnInstanceHandler),
        (r"/participants", ParticipantHandler),
        (r"/healthcheck", HealthCheckHandler)
    ])

    try:
        instance.listen(port)
        print("Survey Response Interface Handler listening on " + str(port))
    except OSError:
        print(str(port) + " already bound")