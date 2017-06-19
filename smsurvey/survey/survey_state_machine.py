import time
import boto3

from enum import Enum
from botocore.exceptions import ClientError


class SurveyStatus(Enum):
    CREATED = 0
    AWAITING_USER_RESPONSE = 1
    PROCESSING_USER_RESPONSE = 2
    TERMINATED_COMPLETE = 3
    TERMINATED_ERROR = 4
    TERMINATED_EXCEPTION = 5
    TERMINATED_TIMEOUT = 6


class SurveyState:
    def __init__(self, event_id, survey_id, next_question, survey_status=SurveyStatus.CREATED,
                 timestamp=int(time.time()), timeout=3600, survey_state_version=1):
        self.event_id = event_id
        self.survey_id = survey_id
        self.next_question = next_question
        self.survey_status = survey_status
        self.timestamp = timestamp
        self.timeout = timeout
        self.survey_state_version = survey_state_version

    @classmethod
    def new_state_object(cls, survey_id, next_question, timeout=3600):
        str_survey_id = str(survey_id)
        event_id = str_survey_id + "_" + str(next_question)
        return cls(event_id, str_survey_id, next_question, timeout=timeout)

    @classmethod
    def from_item(cls, item):
        return cls(item['event_id']['S'], item['survey_id']['S'], int(item['next_question']['N']),
                   SurveyStatus(int(item['survey_status']['N'])), int(item['timestamp']['N']),
                   int(item['timeout']['N']), int(item['survey_state_version']['N']))

    def __eq__(self, other):
        if self.event_id != other.event_id:
            return False
        if self.survey_id != other.survey_id:
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


class SurveyStateService:
    def __init__(self, cache_url, cache_name):
        self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=cache_url)
        self.cache_name = cache_name

    def insert(self, survey_state, safe=True):
        if safe:
            if self.get(survey_state.event_id) is not None:
                raise SurveyCacheOperationException("Key exists")

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'event_id': {
                    'S': survey_state.event_id
                },
                'survey_id': {
                    'S': survey_state.survey_id
                },
                'survey_status': {
                    'N': str(survey_state.survey_status.value)
                },
                'next_question': {
                    'N': str(survey_state.next_question)
                },
                'timestamp': {
                    'N': str(survey_state.timestamp)
                },
                'timeout': {
                    'N': str(survey_state.timeout)
                },
                'survey_state_version': {
                    'N': str(survey_state.survey_state_version)
                }
            }
        )

    def get(self, key):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'event_id': {"S": key},
                    'survey_id': {"S": key[0:key.find('_')]}
                },
                ConsistentRead=True,
                ReturnConsumedCapacity="False"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Item' in response:
                return SurveyState.from_item(response['Item'])
            else:
                return None

    def update(self, key, survey_state, safe=True):
        existing = self.get(key)
        if safe:
            if existing is None:
                raise SurveyCacheOperationException("Specified key is invalid, does not exist")
            if key != survey_state.event_id:
                raise SurveyCacheOperationException("Specified key is invalid, does not match")

            if existing.survey_id != survey_state.survey_id:
                raise SurveyCacheOperationException("Invalid update")
            if existing.survey_state_version != survey_state.survey_state_version:
                raise SurveyCacheOperationException("Invalid update")
            if existing.next_question != survey_state.next_question:
                raise SurveyCacheOperationException("Invalid update")

        self.insert(survey_state, False)

    def delete(self, key, safe=True):
        if safe:
            if self.get(key) is None:
                raise SurveyCacheOperationException("Specified key does not exist in cache")

        self.dynamo.delete_item(
            TableName=self.cache_name,
            Key={
                'event_id': {'S': key},
                'survey_id': {'S': key[0:key.find('_')]}
            }
        )


class SurveyCacheOperationException(Exception):
    """
    Exception Raised when performing a CRUD operation on the cache
    """

    def __init__(self, message):
        self.message = message