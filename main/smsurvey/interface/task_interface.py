import json
import pytz

from tornado.web import RequestHandler
from datetime import datetime, timedelta

from smsurvey.config import logger
from smsurvey.core.security.permissions import Permissions, authenticate
from smsurvey.core.services.task_service import TaskService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.protocol_service import ProtocolService
from smsurvey.schedule.time_rule.time_rule import NoRepeat, RepeatsDaily, RepeatsWeekly, RepeatsMonthlyDate, \
    RepeatsMonthlyDay
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService
from smsurvey.interface.datamanagement import DataManagement
from smsurvey.core.services.participant_service import ParticipantService

class AllTasksHandler(RequestHandler):

    def get(self):
        logger.debug("Querying for tasks")
        auth = authenticate(self, [Permissions.READ_TASK])

        if auth["valid"]:
            surveys = SurveyService.get_surveys_by_owner(auth["owner_id"])

            surveys_tasks = {}

            for survey in surveys:
                surveys_tasks[survey] = TaskService.get_tasks_by_survey_id(survey.id)

            tasks = []

            for survey, task_list in surveys_tasks.items():
                for task in task_list:
                    tasks.append({
                        "id": task.id,
                        "name": task.name,
                        "protocol_name": ProtocolService.get_protocol(survey.protocol_id).name,
                        "enrollment_name": EnrollmentService.get(survey.enrollment_id).name
                    })

            response = {
                "status": "success",
                "tasks": tasks
            }
            self.set_status(200)

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def post(self):
        logger.debug("Posting new task")

        task_name = self.get_argument("name")
        protocol_id = int(self.get_argument("protocol_id"))
        enrollment_id = int(self.get_argument("enrollment_id"))
        time_rule = json.loads(self.get_argument("time_rule"))
        enable_notes = self.get_argument("enable_notes", False)
        timeout = int(self.get_argument("timeout"), 20)
        enable_warnings = self.get_argument("enable_warnings", True)
        enable_notes = 1 if enable_notes else 0
        enable_warnings = 1 if enable_warnings else 0

        all_run_times = []
        all_run_dates = []
        local_tz = pytz.timezone (time_rule['timezone'])
        date_conversion = time_rule["run_date"]
        time_conversion = time_rule["run_times"]
        for several_run_time in time_conversion:
            datetime_without_tz = datetime.strptime(str(date_conversion) + " " + str(several_run_time), "%Y-%m-%d %H:%M")
            datetime_with_tz = local_tz.localize(datetime_without_tz, is_dst=True) # No daylight saving time
            datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)
            str_utc_time = datetime_in_utc.strftime('%Y-%m-%d %H:%M %Z')
            all_run_dates.append(str_utc_time[:10])
            all_run_times.append(str_utc_time[11:16])

        time_rule["run_date"] = str_utc_time[:10]
        time_rule["run_times"] = all_run_times

        auth = authenticate(self, [Permissions.WRITE_TASK, Permissions.WRITE_SURVEY])

        if auth["valid"]:
            owner_id = int(auth['owner_id'])
            response = None

            if ProtocolService.is_owned_by(protocol_id, int(auth['owner_id'])):
                if EnrollmentService.is_owned_by(enrollment_id, owner_id):
                    params = time_rule["params"]
                    run_time_values = time_rule["run_times"]


                    run_times = []

                    for run_time_value in run_time_values:
                        rtv = run_time_value.split(":")
                        hour = int(rtv[0])
                        minute = int(rtv[1])
                        run_times.append(datetime.now(tz=pytz.utc).replace(hour=hour, minute=minute, second=0))
                    until = datetime.strptime(time_rule["run_date"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                    run_date = datetime.strptime(time_rule["run_date"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                    last_date = datetime.strptime(time_rule["run_date"], "%Y-%m-%d")
                    start_date = datetime.strptime(time_rule["run_date"], "%Y-%m-%d")
                    intervalcount = 'no_repeat'
                    if time_rule["type"] == 'no_repeat':
                        intervalcount = 'no_repeat'
                        time_rule = NoRepeat(run_date, run_times)
                    elif time_rule["type"] == 'daily':
                        intervalcount = 'daily'
                        every = int(params["every"])
                        until = datetime.strptime(time_rule['until'], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                        last_date = datetime.strptime(time_rule['until'], "%Y-%m-%d")
                        time_rule = RepeatsDaily(run_date, every, until, run_times)
                    elif time_rule["type"] == 'weekly':
                        intervalcount = 'weekly'
                        every = int(params["every"])
                        until = datetime.strptime(time_rule['until'], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                        time_rule = RepeatsWeekly(every, params['days'], run_times, run_date, until)
                    elif time_rule["type"] == 'monthly_date':
                        intervalcount = 'monthly_date'
                        every = int(params["every"])
                        until = datetime.strptime(time_rule['until'], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                        time_rule = RepeatsMonthlyDate(every, params['dates'], until, run_times)
                    elif time_rule["type"] == 'monthly_day':
                        intervalcount = 'monthly_day'
                        every = int(params["every"])
                        until = datetime.strptime(time_rule['until'], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                        time_rule = RepeatsMonthlyDay(every, params['param1'], params['days'], until, run_times)
                    else:
                        response = {
                            "status": "error",
                            "message": time_rule['type'] + " is not a valid time rule"
                        }
                        self.set_status(400)

                    for daysNo in range((last_date - start_date).days + 1):
                        DataManagement.dataStorage.append(enrollment_id)
                        listParticipants = []
                        participants = ParticipantService.get_participants_in_enrollment(enrollment_id)
                        for participant in participants:
                            listParticipants.append(participant.id)
                        DataManagement.dataStorage.append(listParticipants)
                        DataManagement.dataStorage.append(start_date)
                        DataManagement.dataStorage.append(run_time_values)
                        DataManagement.dataStorage.append("cig_ecig")
                        DataManagement.dataStorage.append(until)
                        DataManagement.dataStorage.append(intervalcount)
                        DataManagement.dataStorage.append(protocol_id)
                        DataManagement.dataStorage.append("scheduled")
                        DataManagement.get_schedule()
                        start_date = start_date + timedelta(days=every)
                else:
                    response = {
                        "status": "error",
                        "message": "Enrollment not owned by account"
                    }
                    self.set_status(401)
            else:
                response = {
                    "status": "error",
                    "message": "Protocol not owned by account"
                }
                self.set_status(401)

            if response is None:
                survey = SurveyService.create_survey(owner_id, protocol_id, enrollment_id, enable_notes, timeout,
                                                     enable_warnings)
                time_rule_id = TimeRuleService().insert(survey.id, time_rule)
                TaskService.create_task(task_name, survey.id, time_rule_id)
                DataManagement.getSurveyid(survey.id)
                response = {
                    "status": "success"
                }
                self.set_status(200)

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass


class ATaskHandler(RequestHandler):

    def get(self, task_id):
        auth = authenticate(self, [Permissions.READ_TASK])

        if auth['valid']:
            task = TaskService.get_task(int(task_id))
            survey = SurveyService.get_survey(task.survey_id)

            if survey.owner_id == int(auth['owner_id']):
                time_rule = TimeRuleService().get(survey.id, task.time_rule_id)
                date_times = time_rule.get_date_times()

                dts = []

                for dt in date_times:

                    hour_str = str(dt.hour) if dt.hour > 9 else '0' + str(dt.hour)
                    minute_str = str(dt.minute) if dt.minute > 9 else '0' + str(dt.minute)

                    dts.append({
                        "year": dt.year,
                        "month": dt.month,
                        "day": dt.day,
                        "time": hour_str + ":" + minute_str
                    })

                response = {
                    "status": "success",
                    "run_times": dts
                }
                self.set_status(200)
            else:
                response = {
                    "status": "error",
                    "message": "Plugin is not registered by survey administrator"
                }
                self.set_status(403)

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def delete(self, task_id):
        logger.debug("Trying to delete a task")
        auth = authenticate(self, [Permissions.READ_TASK])

        if auth['valid']:
            task = TaskService.get_task(int(task_id))
            survey = SurveyService.get_survey(task.survey_id)

            if survey.owner_id == int(auth['owner_id']):
                TaskService.delete_task(task.id)

                self.set_status(200)

                response = {
                    "status": "success"
                }
            else:
                response = {
                    "status": "error",
                    "message": "Plugin is not registered by survey administrator"
                }
                self.set_status(403)

            response_json = json.dumps(response)
            logger.debug(response_json)
            self.write(response_json)
            self.flush()

    def data_received(self, chunk):
        pass
