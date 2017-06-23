import time

from enum import Enum


class SurveyStatus(Enum):
    CREATED = 0
    AWAITING_USER_RESPONSE = 1
    PROCESSING_USER_RESPONSE = 2
    TERMINATED_COMPLETE = 3
    TERMINATED_ERROR = 4
    TERMINATED_EXCEPTION = 5
    TERMINATED_TIMEOUT = 6


class SurveyState:
    def __init__(self, event_id, survey_instance_id, next_question, survey_status=SurveyStatus.CREATED,
                 timestamp=int(time.time()), timeout=3600, survey_state_version=1):
        self.event_id = event_id
        self.survey_instance_id = survey_instance_id
        self.next_question = next_question
        self.survey_status = survey_status
        self.timestamp = timestamp
        self.timeout = timeout
        self.survey_state_version = survey_state_version

    @classmethod
    def new_state_object(cls, survey_instance_id, next_question, timeout=3600):
        str_survey_instance_id = str(survey_instance_id)
        event_id = str_survey_instance_id + "_" + str(next_question)
        return cls(event_id, str_survey_instance_id, next_question, timeout=timeout)

    @classmethod
    def from_item(cls, item):
        return cls(item['event_id']['S'], item['survey_instance_id']['S'], int(item['next_question']['N']),
                   SurveyStatus(int(item['survey_status']['N'])), int(item['timestamp']['N']),
                   int(item['timeout']['N']), int(item['survey_state_version']['N']))

    def __eq__(self, other):
        if self.event_id != other.event_id:
            return False
        if self.survey_instance_id != other.survey_instance_id:
            return False
        if self.next_question != other.next_question:
            return False
        if self.survey_status != other.survey_status:
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
