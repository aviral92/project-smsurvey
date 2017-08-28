import pickle

import boto3
from botocore.exceptions import ClientError

from smsurvey.core.model.response_set import ResponseSet
from smsurvey import config


class ResponseService:

    def __init__(self, cache_name=config.response_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def get_response_set(self, survey_id, instance_id):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'survey_id': {'S': str(survey_id)},
                    'instance_id': {'S': str(instance_id)}
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                response_dict = pickle.loads(response['Item']['responses']['B'])

                return ResponseSet(survey_id, instance_id, response_dict)

    def insert_response(self, survey_id, instance_id, variable_name, message):
        response = self.get_response_set(survey_id,instance_id)

        if response is None:
            response = ResponseSet(survey_id, instance_id)

        response.add_response(variable_name, message)

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'survey_id': {
                    'S': str(survey_id)
                },
                'instance_id': {
                    'S': str(instance_id)
                },
                'responses': {
                    'B': pickle.dumps(response.response_dict)
                }
            }
        )
