import pickle

import boto3
from botocore.exceptions import ClientError

s


class QuestionService:

    def __init__(self, cache_name=config.question_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def insert(self, question_id, question, safe=True):
        if not issubclass(type(question), Question):
            raise QuestionOperationException("Object is not a survey question")

        if question_id.find("_") is -1:
            raise QuestionOperationException("Invalid question key")

        if safe:
            if self.get(question_id) is not None:
                raise QuestionOperationException("Question with this ID already exists in cache")

        dumped = pickle.dumps(question)

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'question_id': {
                    'S': question_id
                },
                'survey_id': {
                    'S': question_id[0:question_id.find("_")]
                },
                'question': {
                    'B': dumped
                }
            }
        )

    def get(self, question_id):
        if question_id.find("_") is -1:
            raise QuestionOperationException("Invalid question key")

        survey_id = question_id[0:question_id.find("_")]

        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'question_id': {'S': question_id},
                    'survey_id': {'S': survey_id}
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
