from datetime import datetime

import pytz
from apscheduler.schedulers.tornado import TornadoScheduler

from smsurvey.core.services.task_service import TaskService
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService

schedule = None


def instance_start(survey_id):
    print("Creating instance for survey_id [" + str(survey_id) + "]")
    instance = InstanceService.create_instance(survey_id)
    print("instance_id [" + str(instance.instance_id) + "] created for survey_id [" + str(survey_id) + "]")


def add_job(survey_id, date_time):
    global schedule

    if schedule is not None:
        schedule.add_job(instance_start, 'date', run_date=date_time, args=[survey_id])
        print(survey_id + " scheduled for " + date_time.strftime("%Y-%m-%d %H:%M:%S %Z"))


def load_persisted_tasks():
    tasks = TaskService.get_all_tasks()

    time_rule_service = TimeRuleService()

    for task in tasks:
        time_rule = time_rule_service.get(task.survey_id, task.time_rule_id)
        date_times = time_rule.get_date_times()

        for dt in date_times:
            dt = dt.replace(tzinfo=pytz.utc)
            if dt > datetime.now(pytz.utc):
                add_job(task.survey_id, dt)
            else:
                print(dt.strftime("%Y-%m-%d %H:%M:%S %Z") + " is in the past for survey " + task.survey_id)


def start_schedule():
    global schedule
    if schedule is None:
        print("Starting schedule")
        schedule = TornadoScheduler()
        schedule.start()
        print("Hydrating schedule")
        load_persisted_tasks()
        print("Schedule running")
    else:
        print("Schedule was already running")
