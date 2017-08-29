import pickle

import boto3
from botocore.exceptions import ClientError

from smsurvey.core.model.question import Question
from smsurvey.core.model.question import QuestionOperationException
from smsurvey import config


class QuestionService:

    def __init__(self, cache_name=config.question_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def insert(self, protocol_id, question_number, question, safe=True):
        if not issubclass(type(question), Question):
            raise QuestionOperationException("Object is not a survey question")

        if safe:
            if self.get(protocol_id, question_number) is not None:
                raise QuestionOperationException("Question with this ID already exists in cache")

        dumped = pickle.dumps(question)

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'question_number': {
                    'S': str(question_number)
                },
                'protocol_id': {
                    'S': str(protocol_id)
                },
                'question': {
                    'B': dumped
                }
            }
        )

    def get(self, protocol_id, question_number):

        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'question_number': {'S': str(question_number)},
                    'protocol_id': {'S': str(protocol_id)}
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise QuestionOperationException("Error occurred trying to get item")
        else:
            if 'Item' in response:
                return pickle.loads(response['Item']['question']['B'])
            else:
                return None
