from datetime import datetime

import pytz
from apscheduler.schedulers.tornado import TornadoScheduler


from smsurvey.config import logger
from smsurvey.core.services.task_service import TaskService
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService

schedule = None


def instance_start(survey_id):
    logger.info("Creating instances for survey_id %s", str(survey_id))
    instances = InstanceService.create_instances(survey_id)
    instance_ids = [instance.id for instance in instances]
    logger.info("instance_ids %s created for survey_id %s", str(instance_ids), str(survey_id))


def add_job(survey_id, date_time):
    global schedule

    if schedule is not None:
        schedule.add_job(instance_start, 'date', run_date=date_time, args=[survey_id])
        logger.info("%s scheduled for %s", str(survey_id), date_time.strftime("%Y-%m-%d %H:%M:%S %Z"))


def load_persisted_tasks():
    tasks = TaskService.get_all_tasks()

    if tasks is None:
        return

    time_rule_service = TimeRuleService()

    for task in tasks:
        time_rule = time_rule_service.get(task.survey_id, task.time_rule_id)
        date_times = time_rule.get_date_times()

        for dt in date_times:
            dt = dt.replace(tzinfo=pytz.utc)
            if dt > datetime.now(pytz.utc):
                add_job(task.survey_id, dt)
            else:
                logger.warning("%s is in the past for survey %s", dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
                               str(task.survey_id))


def load_maintenance_jobs():
    logger.info("Loading ")


def start_schedule():
    global schedule
    if schedule is None:
        logger.info("Launching scheduler")
        schedule = TornadoScheduler()
        schedule.start()
        logger.info("Hydrating schedule with surveys")
        load_persisted_tasks()
        logger.info("Loading maintenance jobs into schedule")

        logger.info("Schedule running")

    else:
        logger.info("Schedule was already running")
