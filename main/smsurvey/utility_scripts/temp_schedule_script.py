
import os
import pytz
import sys
import inspect
import time as t

from datetime import datetime, timedelta, time

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey.core.model.survey.survey import Survey
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.state_service import StateService
from smsurvey.schedule.time_rule.time_rule import RepeatsDailyTimeRule
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService
from smsurvey.schedule.schedule_service import ScheduleService

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

print("Generating and inserting surveys")

survey_service = SurveyService()
participant_service = ParticipantService()
instance_service = InstanceService()
state_service = StateService()
i = 0
for survey in surveys:
    i += 1
    survey_id = str(t.time() + i)

    participant_service.register_participant(survey["participant_id"], survey["plugin_id"], survey["plugin_scratch"])
    survey_object = Survey(survey_id, '1', survey["participant_id"], "owner", "test")
    survey_service.insert(survey_object)

    starting_from = datetime.now()
    every = 1
    until = starting_from + timedelta(days=100)
    run_at1 = time(tzinfo=pytz.utc).replace(hour=10, minute=25, second=0, microsecond=0)
    run_at2 = time(tzinfo=pytz.utc).replace(hour=10, minute=30, second=0, microsecond=0)
    tr1 = RepeatsDailyTimeRule(starting_from, every, until, run_at1)
    tr2 = RepeatsDailyTimeRule(starting_from, every, until, run_at2)

    time_rule_id1 = TimeRuleService().insert(survey_id, tr1, survey_id + "1")
    time_rule_id2 = TimeRuleService().insert(survey_id, tr2, survey_id + "2")

    ScheduleService().insert_task(survey_id, time_rule_id1)
    ScheduleService().insert_task(survey_id, time_rule_id2)


print("Surveys inserted and generated")

print("Script finished")
