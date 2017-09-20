import time
import pytz

from datetime import datetime
from apscheduler.schedulers.tornado import TornadoScheduler


from smsurvey.config import logger
from smsurvey.core.services.task_service import TaskService
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService

schedule = None
latest_task = None
all_tasks = []


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


def load_tasks(tasks):
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


def load_persisted_tasks():
    tasks = TaskService.get_all_tasks()
    if len(tasks) > 0:
        load_tasks(tasks)
        global latest_task
        latest_task = tasks[-1]


def check_for_new_tasks():
    logger.info("Checking if new jobs are waiting to be scheduled")
    global latest_task
    if latest_task is None:
        load_persisted_tasks()
    else:
        tasks = TaskService.get_tasks_since(latest_task)
        logger.info("%s new tasks to be scheduled", str(len(tasks)))
        if len(tasks) > 0:
            load_tasks(tasks)
            latest_task = tasks[-1]


def check_for_removed_tasks():
    logger.info("Cleaning schedule, removing any deleted tasks")
    global schedule
    schedule.shutdown()
    schedule = None
    start_schedule()


def start_schedule():
    global schedule
    if schedule is None:
        logger.info("Launching scheduler")
        schedule = TornadoScheduler()
        schedule.start()
        logger.info("Hydrating schedule with surveys")
        load_persisted_tasks()
        logger.info("Preparing maintenance jobs for updating schedule (adding and removing)")
        schedule.add_job(check_for_new_tasks, 'interval', minutes=5)
        schedule.add_job(check_for_removed_tasks, 'interval', minutes=30)
    else:
        logger.info("Schedule was already running")
