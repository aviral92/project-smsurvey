from tornado.web import Application, RequestHandler

from smsurvey.config import logger
from smsurvey.interface.survey_interface import AllInstancesHandler, LatestQuestionHandler, AQuestionHandler,\
    AnInstanceHandler
from smsurvey.interface.participant_interface import ParticipantHandler
from smsurvey.interface.enrollment_interface import AllEnrollmentsHandler, AnEnrollmentHandler,\
    AnEnrollmentAllParticipantsHandler, AnEnrollmentAParticipantHandler


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
        (r"/enrollments", AllEnrollmentsHandler),
        (r"/enrollments/(\d*)", AnEnrollmentHandler),
        (r"/enrollments/(\d*)/enrolled", AnEnrollmentAllParticipantsHandler),
        (r"/enrollments/(\d*)/(\d*)", AnEnrollmentAParticipantHandler),
        (r"/healthcheck", HealthCheckHandler)
    ])

    try:
        instance.listen(port)
        logger.info("Survey Response Interface Handler listening on " + str(port))
    except OSError:
        logger.error(str(port) + " already bound, terminating process")
        exit(1)
