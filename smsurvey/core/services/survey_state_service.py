import boto3

from botocore.exceptions import ClientError

from smsurvey.core.model.survey.survey_state_machine import SurveyStateOperationException
from smsurvey.core.model.survey.survey_state_machine import SurveyState


class SurveyStateService:

    def __init__(self, cache_url, cache_name):
        self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=cache_url)
        self.cache_name = cache_name

    def insert(self, survey_state, safe=True):
        if safe:
            if self.get(survey_state.event_id) is not None:
                raise SurveyStateOperationException("Key exists")

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'event_id': {
                    'S': survey_state.event_id
                },
                'survey_instance_id': {
                    'S': survey_state.survey_instance_id
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
                    'survey_instance_id': {"S": key[0:key.find('_')]}
                },
                ConsistentRead=True,
                ReturnConsumedCapacity="False"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                return SurveyState.from_item(response['Item'])
            else:
                return None

    def update(self, key, survey_state, safe=True):
        existing = self.get(key)
        if safe:
            if existing is None:
                raise SurveyStateOperationException("Specified key is invalid, does not exist")
            if key != survey_state.event_id:
                raise SurveyStateOperationException("Specified key is invalid, does not match")

            if existing.survey_instance_id != survey_state.survey_instance_id:
                raise SurveyStateOperationException("Invalid update")
            if existing.survey_state_version != survey_state.survey_state_version:
                raise SurveyStateOperationException("Invalid update")
            if existing.next_question != survey_state.next_question:
                raise SurveyStateOperationException("Invalid update")

        self.insert(survey_state, False)

    def delete(self, key, safe=True):
        if safe:
            if self.get(key) is None:
                raise SurveyStateOperationException("Specified key does not exist in cache")

        self.dynamo.delete_item(
            TableName=self.cache_name,
            Key={
                'event_id': {'S': key},
                'survey_instance_id': {'S': key[0:key.find('_')]}
            }
        )

    def get_by_instance_and_status(self, survey_instance_id, survey_status, last_key=None):
        try:
            response = self.dynamo.query(
                TableName=self.cache_name,
                IndexName='SurveyStatus',
                ConsisentRead=True,
                KeyConditions={
                    'survey_instance_id': {
                        'ComparisonOperator': 'EQ',
                        'AttributeValueList': [survey_instance_id]
                    },
                    'survey_status': {
                        'ComparisonOperator': 'EQ',
                        'AttributeValueList': [survey_status]
                    }
                },
                ExclusiveStartKey=last_key
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            if 'Items' in response:
                return SurveyState.from_item(response['Items'][0])
            elif 'LastEvaluatedKey' in response:
                return self.get_by_instance_and_status(survey_instance_id, survey_status, response['LastEvaluatedKey'])
