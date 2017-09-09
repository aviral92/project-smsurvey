import json

from tornado.web import RequestHandler

from smsurvey.config import logger
from smsurvey.core.security.permissions import Permissions, authenticate
from smsurvey.core.services.task_service import TaskService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.protocol_service import ProtocolService


class AllTasksHandler(RequestHandler):

    def get(self):
        logger.debug("Querying for tasks")
        auth = authenticate(self, [Permissions.READ_TASK])

        if auth["valid"]:
            surveys = SurveyService.get_surveys_by_owner(auth["owner_id"])

            task_objects = []

            for survey in surveys:
                task_objects += (TaskService.get_tasks_by_survey_id(survey.id), survey)

            tasks = []

            for task_object in task_objects:
                task = {
                    "name": task_object[0].name,
                    "protocol_name": ProtocolService.get_protocol(task_object[0].protocol_id).name,
                    "enrollment_name": EnrollmentService.get(task_object[1].enrollment_id).name
                }

                tasks.append(task)

            response = {
                "status": "success",
                "tasks": tasks
            }
            self.set_status(200)

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()



    def data_received(self, chunk):
        pass

