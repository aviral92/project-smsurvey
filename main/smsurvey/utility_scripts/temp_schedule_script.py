import inspect
import os
import sys
import pytz
from datetime import datetime, timedelta, time


c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey import config
from smsurvey.core.model.model import Model
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.services.protocol_service import ProtocolService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.task_service import TaskService
from smsurvey.schedule.time_rule.time_rule import RepeatsDailyTimeRule
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService

print("Loading models")
Model.from_database(config.dao)

print("Generating and inserting surveys")

owner = OwnerService.get("sam", "mhealth")

enrollment = EnrollmentService.get_by_owner(owner.id)[0]
survey = SurveyService.create_survey(owner.id, ProtocolService.get_all_protocols()[0].id, enrollment.id, False)

starting_from = datetime.now()
every = 1
until = starting_from + timedelta(days=1)
run_at = time(tzinfo=pytz.utc).replace(hour=16, minute=35, second=0, microsecond=0)
tr = RepeatsDailyTimeRule(starting_from, every, until, [run_at])
time_rule_id = TimeRuleService().insert(survey.id, tr, str(survey.id) + "1")
TaskService.create_task("Demo task", survey.id, time_rule_id)

print("Surveys inserted and generated")

print("Script finished")
