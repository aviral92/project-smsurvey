from enum import Enum


class Status(Enum):
    CREATED_START = 100
    CREATED_MID = 200
    AWAITING_USER_RESPONSE = 300
    PROCESSING_USER_RESPONSE = 400
    TERMINATED_COMPLETE = 500
    TERMINATED_ERROR = 600
    TERMINATED_EXCEPTION = 700
    TERMINATED_TIMEOUT = 800


class State:

    def __init__(self, state_id, instance_id, question_id, status, priority):
        self.state_id = state_id
        self.instance_id = instance_id
        self.question_id = question_id
        self.status = Status(status)
        self.priority = priority

    @classmethod
    def from_tuple(cls, state_tuple):
        return cls(state_tuple[0], state_tuple[1], state_tuple[2], state_tuple[3], state_tuple[4])

    def __eq__(self, other):
        if self.state_id != other.state_id:
            return False
        if self.instance_id != other.instance_id:
            return False
        if self.question_id != other.question_id:
            return False
        if self.status != other.survey_status:
            return False
        if self.priority != other.priority:
            return False

        return True


class StateException(Exception):

    def __init__(self, message):
        self.message = message
