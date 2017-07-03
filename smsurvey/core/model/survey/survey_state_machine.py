import time

from enum import Enum


class SurveyStatus(Enum):
    CREATED_START = 100
    CREATED_MID = 200
    AWAITING_USER_RESPONSE = 300
    PROCESSING_USER_RESPONSE = 400
    TERMINATED_COMPLETE = 500
    TERMINATED_ERROR = 600
    TERMINATED_EXCEPTION = 700
    TERMINATED_TIMEOUT = 800


class SurveyState:
    def __init__(self, event_id, survey_instance_id, owner, next_question, survey_status=SurveyStatus.CREATED_START,
                 priority=0, timestamp=int(time.time()), timeout=3600, survey_state_version=1):
        self.event_id = event_id
        self.survey_instance_id = survey_instance_id
        self.owner = owner
        self.next_question = next_question
        self.survey_status = survey_status
        self.priority = priority
        self.timestamp = timestamp
        self.timeout = timeout
        self.survey_state_version = survey_state_version

    @classmethod
    def new_state_object(cls, survey_instance_id, owner, next_question, priority=0, timeout=3600):
        str_survey_instance_id = str(survey_instance_id)
        event_id = str_survey_instance_id + "_" + str(next_question)
        return cls(event_id, str_survey_instance_id, owner, next_question, priority=priority, timeout=timeout)

    @classmethod
    def from_item(cls, item):
        return cls(item['event_id']['S'], item['survey_instance_id']['S'], item['survey_owner']['S'],
                   item['next_question']['S'], SurveyStatus(int(item['survey_status']['N'])), int(item['priority']['N']),
                   int(item['timestamp']['N']), int(item['timeout']['N']), int(item['survey_state_version']['N']))

    def __eq__(self, other):
        if self.event_id != other.event_id:
            return False
        if self.survey_instance_id != other.survey_instance_id:
            return False
        if self.owner != other.owner:
            return False
        if self.next_question != other.next_question:
            return False
        if self.survey_status != other.survey_status:
            return False
        if self.priority != other.priority:
            return False
        if self.timestamp != other.timestamp:
            return False
        if self.timeout != other.timeout:
            return False
        if self.survey_state_version != other.survey_state_version:
            return False

        return True

class SurveyStateOperationException(Exception):

    def __init__(self, message):
        self.message = message
