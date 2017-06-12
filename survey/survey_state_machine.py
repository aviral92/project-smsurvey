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

    def __init__(self, survey_id, next_question, timeout=3600):
        self.event_id = survey_id + "_" + next_question
        self.survey_id = survey_id
        self.survey_status = SurveyStatus.CREATED
        self.next_question = next_question
        self.timestamp = int(time.time())
        self.timeout = timeout
