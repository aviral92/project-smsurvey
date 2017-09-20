from tornado.web import Application, RequestHandler, StaticFileHandler

from smsurvey.config import logger
from smsurvey.interface.survey_interface import AllInstancesHandler, LatestQuestionHandler, AQuestionHandler,\
    AnInstanceHandler
from smsurvey.interface.participant_interface import ParticipantHandler
from smsurvey.interface.enrollment_interface import AllEnrollmentsHandler, AnEnrollmentHandler,\
    AnEnrollmentAllParticipantsHandler, AnEnrollmentAParticipantHandler
from smsurvey.console.login_interface import LoginHandler, LogoutHandler, CheckLoginHandler
from smsurvey.console.console_interface import PluginsRequestHandler, PluginPermissionsHandler, \
    UnregisteredPluginPermissionsHandler
from smsurvey.interface.plugin_interface import AllPluginsHandler
from smsurvey.interface.task_interface import AllTasksHandler, ATaskHandler
from smsurvey.interface.protocol_interface import AllProtocolsHandler


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
        (r"/plugins", AllPluginsHandler),
        (r"/tasks/(\d*)", ATaskHandler),
        (r"/tasks", AllTasksHandler),
        (r"/protocols", AllProtocolsHandler),
        (r"/console/login", LoginHandler),
        (r"/console/logout", LogoutHandler),
        (r"/console/check_login", CheckLoginHandler),
        (r"/console/plugins", PluginsRequestHandler),
        (r"/console/plugins/(\d*)/permissions", PluginPermissionsHandler),
        (r"/console/plugins/(.*)/permissions", UnregisteredPluginPermissionsHandler),
        (r"/healthcheck", HealthCheckHandler),
        (r"/(.*)", StaticFileHandler,
         {"path": "smsurvey/static/console/", "default_filename": "index.html"})
    ])

    try:
        instance.listen(port)
        logger.info("Survey Response Interface Handler listening on " + str(port))
    except OSError:
        logger.error(str(port) + " already bound, terminating process")
        exit(1)
