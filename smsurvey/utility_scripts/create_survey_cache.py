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
                'AttributeName': 'participant',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'survey_id',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'participant',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'survey_id',
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print("Cache status: ", survey_cache['TableDescription']['TableStatus'])


if __name__ == "__main__":
    if config.survey_backend_name in dynamo.list_tables()['TableNames']:
        while True:
            answer = input(config.survey_backend_name + " already exists. Delete existing and create new? (Yes/n)")

            if answer == 'n':
                exit(0)
            elif answer == 'Yes':
                dynamo.delete_table(TableName=config.survey_backend_name)
                break

    create_cache(config.survey_backend_name)
