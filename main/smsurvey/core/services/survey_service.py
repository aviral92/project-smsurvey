import boto3

from botocore.exceptions import ClientError

from smsurvey import config
from smsurvey.core.model.survey.survey import Survey
from smsurvey.core.model.survey.survey import SurveyOperationException


class SurveyService:

    def __init__(self, cache_name=config.survey_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def get_survey(self, survey_id, survey_instance_id):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'survey_id': {'S': survey_id},
                    'participant': {'S': survey_instance_id}
                },
                ConsistentRead=True,
                ReturnConsumedCapacity='NONE'
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                return Survey.from_item(response['Item'])
            else:
                return None

    def insert(self, survey, safe=True):
        if safe:
            if self.get_survey(survey.survey_id, survey.survey_instance_id) is not None:
                raise SurveyOperationException("Key exists")

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'survey_id': {
                    'S': survey.survey_id
                },
                'survey_instance_id': {
                    'S': survey.survey_instance_id
                },
                'owner': {
                    'S': survey.owner
                },
                'participant_id': {
                    'S': survey.participant_id
                },
                'participant_payload': {
                    'S': survey.participant_payload
                }
            }
        )
