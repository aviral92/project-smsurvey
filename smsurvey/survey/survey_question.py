import boto3
import pickle

from botocore.exceptions import ClientError


class SurveyQuestion:

    # Return a String that asks your question
    def ask_question(self):
        raise NotImplementedError("Implement in own class")

    # Process a response, and returns a new survey state
    def process_response(self, response):
        raise NotImplementedError("Implement in own class")


class QuestionService:

    def __init__(self, cache_url, cache_name):
        self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=cache_url)
        self.cache_name = cache_name

    def insert(self, question_id, question, safe=True):
        if not issubclass(type(question), SurveyQuestion):
            raise QuestionServiceOperationException("Object is not a survey question")

        if question_id.find("_") is -1:
            raise QuestionServiceOperationException("Invalid question key")

        if safe:
            if self.get(question_id) is not None:
                raise QuestionServiceOperationException("Question with this ID already exists in cache")

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
            raise QuestionServiceOperationException("Invalid question key")

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
            raise QuestionServiceOperationException("Error occurred trying to get item")
        else:
            if 'Item' in response:
                return pickle.loads(response['Item']['question']['B'])
            else:
                return None


class QuestionServiceOperationException(Exception):

    def __init__(self, message):
        self.message = message
