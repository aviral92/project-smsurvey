import boto3
import pickle

from botocore.exceptions import ClientError

from smsurvey.core.model.survey.response import Response


class ResponseService:

    def __init__(self, cache_url, cache_name):
        self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=cache_url)
        self.cache_name = cache_name

    def get_response(self, survey_id, survey_instance_id):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'survey_id': {'S': survey_id},
                    'survey_instance_id': {'S': survey_instance_id}
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                response_dict = pickle.loads(response['Item']['responses']['B'])

                return Response(survey_id, survey_instance_id, response_dict)

    def insert_response(self, survey_id, survey_instance_id, variable_name, message):
        response = self.get_response(survey_id,survey_instance_id)

        if response is None:
            response = Response(survey_id, survey_instance_id)
            response.add_response(variable_name, message)

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'survey_id': {
                    'S': survey_id
                },
                'survey_instance_id': {
                    'S': survey_instance_id
                },
                'responses': {
                    'B': pickle.dumps(response.response_dict)
                }
            }
        )
