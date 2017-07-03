from tornado import process
from tornado.web import Application
from tornado.ioloop import IOLoop

from smsurvey import config
from smsurvey.interface.survey_interface import AllSurveysHandler
from smsurvey.interface.survey_interface import LatestQuestionHandler
from smsurvey.interface.survey_interface import AQuestionHandler
from smsurvey.interface.survey_interface import ASurveyHandler


def initiate_interface():
    process_id = process.fork_processes(config.response_interface_processes, max_restarts=0)

    instance = Application([

        (r"/surveys", AllSurveysHandler),
        (r"/surveys/(\d*_*\d*)/latest", LatestQuestionHandler),
        (r"/surveys/(\d*_*\d*)/(\d*_*\d*)", AQuestionHandler),
        (r"/surveys/(\d*_*\d*)", ASurveyHandler),
    ])



    port = config.survey_response_interface_port_begin + process_id
    instance.listen(port)
    print("Survey Response Interface Handler listening on " + str(port))
    IOLoop.current().start()
