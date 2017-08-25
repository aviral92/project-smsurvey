
import inspect
import os
import sys
import pytz
import time as t
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
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.task_service import TaskService
from smsurvey.schedule.time_rule.time_rule import RepeatsDailyTimeRule
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService

phone_numbers = os.environ.get("PHONE_NUMBERS")

surveys = []
i = 1
for phone_number in phone_numbers.split(","):
    surveys.append({
        "instance_id": str(i),
        "participant_id": str(t.time() + i),
        "plugin_id": 1,
        "plugin_scratch": phone_number
    })
    i += 1

print("Loading models")
Model.from_database(config.dao)

print("Generating and inserting surveys")

owner = OwnerService.get("owner", "test")
enrollment = EnrollmentService.add_enrollment("Test Enrollment", owner.id, datetime.now(tz=pytz.utc),
                                              datetime.now(tz=pytz.utc).replace(year=2018),
                                              datetime.now(tz=pytz.utc).replace(year=2019))

i = 0
for survey in surveys:
    i += 1

    ParticipantService.register_participant(enrollment.id, survey["plugin_id"], survey["plugin_scratch"])
    survey_object = SurveyService.create_survey(owner.id, ProtocolService.get_all_protocols()[0].id, enrollment.id)
    survey_id = survey_object.id

    starting_from = datetime.now()
    every = 1
    until = starting_from + timedelta(days=100)
    run_at1 = time(tzinfo=pytz.utc).replace(hour=10, minute=25, second=0, microsecond=0)
    run_at2 = time(tzinfo=pytz.utc).replace(hour=10, minute=30, second=0, microsecond=0)
    tr1 = RepeatsDailyTimeRule(starting_from, every, until, run_at1)
    tr2 = RepeatsDailyTimeRule(starting_from, every, until, run_at2)

    time_rule_id1 = TimeRuleService().insert(survey_id, tr1, str(survey_id) + "1")
    time_rule_id2 = TimeRuleService().insert(survey_id, tr2, str(survey_id) + "2")

    TaskService.create_task(survey_id, time_rule_id1)
    TaskService.create_task(survey_id, time_rule_id2)

print("Surveys inserted and generated")

print("Script finished")
