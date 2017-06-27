from tornado import process
from tornado.web import Application
from tornado.ioloop import IOLoop

from smsurvey import config
from smsurvey.interface.survey_interface import SurveyHandler
from smsurvey.interface.survey_interface import SurveysHandler
from smsurvey.interface.survey_interface import NewSurveyHandler


def initiate_interface():
    process_id = process.fork_processes(config.response_interface_processes, max_restarts=0)

    instance = Application([
        (r"/surveys", SurveysHandler),
        (r"/surveys/(.*)", SurveyHandler),
        (r"/newsurvey/(.*)", NewSurveyHandler)
    ])

    port = config.survey_response_interface_port_begin + process_id
    instance.listen(port)
    print("Survey Response Interface Handler listening on " + str(port))
    IOLoop.current().start()
