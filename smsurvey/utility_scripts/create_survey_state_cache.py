import boto3
import os
import inspect
import sys
import argparse

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey import config

dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)


def create_cache(t_name):
    t = dynamo.create_table(
        TableName=t_name,
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
                'AttributeName': 'survey_owner',
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
                        'AttributeName': 'survey_owner',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'survey_instance_id',
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

    print("Cache status: ", t['TableDescription']['TableStatus'])


def main(force):
    t_name = config.survey_state_backend_name

    if force:
        print("Creating " + t_name + " - FORCED")
        if t_name in dynamo.list_tables()['TableNames']:
            print("Removing old " + t_name)
            dynamo.delete_table(TableName=t_name)
    else:
        if t_name in dynamo.list_tables()['TableNames']:
            while True:
                answer = input(t_name + " already exists. Delete existing and create new? (Yes/n)")

                if answer == 'n':
                    exit(0)
                elif answer == 'Yes':
                    dynamo.delete_table(TableName=t_name)
                    break

    print("Creating " + t_name)
    create_cache(t_name)
    print("Finished creating " + t_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", action="store_true", dest="force")
    args = parser.parse_args()

    main(args.force)
