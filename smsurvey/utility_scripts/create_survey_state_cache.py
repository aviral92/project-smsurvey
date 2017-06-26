import boto3
import os
import inspect
import sys

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey import config

dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)


def create_cache(cache_name):
    survey_cache = dynamo.create_table(
        TableName=cache_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'survey_instance_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'event_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'survey_status',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'owner',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'survey_instance_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'event_id',
                'KeyType': 'RANGE'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'SurveyStatus',
                'KeySchema': [
                    {
                        'AttributeName': 'survey_instance_id',
                        'KeyType': 'HASH'
                    }, {
                        'AttributeName': 'survey_status',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            },
            {
                'IndexName': 'SurveyOwner',
                'KeySchema': [
                    {
                        'AttributeName': 'survey_instance_id',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'owner',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print("Cache status: ", survey_cache['TableDescription']['TableStatus'])


if __name__ == "__main__":
    if config.survey_state_backend_name in dynamo.list_tables()['TableNames']:
        while True:
            answer = input(config.survey_state_backend_name + " already exists. Delete existing? (Yes/n)")

            if answer == 'n':
                exit(0)
            elif answer == 'Yes':
                dynamo.delete_table(TableName=config.survey_state_backend_name)
                break

    create_cache(config.survey_state_backend_name)