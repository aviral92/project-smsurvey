import boto3

from botocore.exceptions import ClientError

from smsurvey import config
from smsurvey.core.model.survey.survey import Survey


class SurveyService:

    def __init__(self, cache_name=config.survey_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def get_survey(self, survey_id, participant):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'survey_id': {'S': survey_id},
                    'participant': {'S': participant}
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
