import os
import pytz

from datetime import datetime, timedelta

from smsurvey.core.model.survey.survey import Survey
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.instance_service import InstanceService
from smsurvey.core.services.state_service import StateService
from smsurvey.schedule.time_rule.time_rule import NoRepeatTimeRule
from smsurvey.schedule.time_rule.time_rule_service import TimeRuleService
from smsurvey.schedule.schedule_service import ScheduleService

phone_numbers = os.environ.get("PHONE_NUMBERS")

surveys = []
i = 1
for phone_number in phone_numbers.split(","):
    surveys.append({
        "instance_id": str(i),
        "participant_id": str(i),
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

    participant_service.register_participant(survey["participant_id"], survey["plugin_id"], survey["plugin_scratch"])
    survey_object = Survey(str(i), '1', survey["participant_id"], "owner", "test")
    survey_service.insert(survey_object)

    time_rule = NoRepeatTimeRule(datetime.now(pytz.utc) + timedelta(minutes=2))
    time_rule_id = TimeRuleService().insert(str(i), time_rule)
    ScheduleService().insert_task(str(i), time_rule_id)

print("Surveys inserted and generated")

print("Script finished")
