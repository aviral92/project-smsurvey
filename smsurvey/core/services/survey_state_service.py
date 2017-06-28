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
            if self.get(survey_state.event_id, survey_state.next_question) is not None:
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
                'survey_owner': {
                    'S': str(survey_state.owner)
                },
                'survey_status': {
                    'N': str(survey_state.survey_status.value)
                },
                'next_question': {
                    'S': str(survey_state.next_question)
                },
                'priority' : {
                    'N': str(survey_state.priority)
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

    def get(self, survey_instance_id, next_question):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'event_id': {"S": survey_instance_id + "_" + next_question},
                    'survey_instance_id': {"S": survey_instance_id}
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

    def update(self, survey_state):
        existing = self.get(survey_state.survey_instance_id, survey_state.next_question)

        if existing.survey_instance_id != survey_state.survey_instance_id:
            raise SurveyStateOperationException("Invalid update - ids must be constant")
        if existing.survey_state_version != survey_state.survey_state_version:
            raise SurveyStateOperationException("Invalid update - version must be constant")
        if existing.next_question != survey_state.next_question:
            raise SurveyStateOperationException("Invalid update - next question must be constant")
        if existing.owner != survey_state.owner:
            raise SurveyStateOperationException("Invalid update - owner must constant")

        self.insert(survey_state, False)

    def delete(self, key):

        self.dynamo.delete_item(
            TableName=self.cache_name,
            Key={
                'event_id': {'S': key},
                'survey_instance_id': {'S': key[0:key.find('_')]}
            }
        )

    def get_by_instance_and_status(self, survey_instance_id, survey_status, last_key=None):
        try:
            print("survey_instance_id = " + survey_instance_id)
            if last_key is None:
                response = self.dynamo.query(
                    TableName=self.cache_name,
                    IndexName='SurveyStatus',
                    ConsistentRead=False,
                    KeyConditionExpression="survey_instance_id = :sid AND survey_status = :status",
                    ExpressionAttributeValues={
                        ":sid": {'S': survey_instance_id},
                        ":status": {'N': str(survey_status.value)}
                    }
                )
            else:
                response = self.dynamo.query(
                    TableName=self.cache_name,
                    IndexName='SurveyStatus',
                    ConsistentRead=False,
                    KeyConditionExpression="survey_instance_id = :sid AND survey_status = :status",
                    ExpressionAttributeValues={
                        ":sid": {'S': survey_instance_id},
                        ":status": {'N': str(survey_status.value)}
                    },
                    ExclusiveStartKey=last_key
                )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print(response)
            if 'Items' in response and len(response['Items']) > 0:
                lowest_priority = int(response['Items'][0]['priority']['N'])
                item = SurveyState.from_item(response['Items'][0])

                for i in response['Items']:
                    priority = int(i['priority']['N'])
                    if priority < lowest_priority:
                        lowest_priority = priority
                        item = SurveyState.from_item(i)

                return item

            elif 'LastEvaluatedKey' in response:
                return self.get_by_instance_and_status(survey_instance_id, survey_status, response['LastEvaluatedKey'])
            else:
                return None

    def get_by_owner(self, survey_owner, survey_status=None, last_key=None):
        try:
            if last_key is None:
                response = self.dynamo.query(
                    TableName=self.cache_name,
                    IndexName='SurveyOwner',
                    ConsistentRead=False,
                    KeyConditionExpression="survey_owner = :so",
                    ExpressionAttributeValues={
                        ":so": {'S': survey_owner}
                    }
                )
            else:
                response = self.dynamo.query(
                    TableName=self.cache_name,
                    IndexName='SurveyOwner',
                    ConsistentRead=False,
                    KeyConditionExpression="survey_owner = :so",
                    ExpressionAttributeValues={
                        ":so": {'S': survey_owner}
                    },
                    ExclusiveStartKey=last_key
                )
        except ClientError as e:
            print("A" + str(e.response['Error']['Message']))
        else:
            if 'Items' in response:
                items = []
                for i in response['Items']:
                    item = SurveyState.from_item(i)
                    if item.survey_status == survey_status:
                        items.append(item.survey_instance_id)

                if 'LastEvaluatedKey' in response:
                    items += self.get_by_owner(survey_owner, survey_status, response['LastEvaluatedKey'])

                return items
            else:
                return []
