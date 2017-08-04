import boto3
import os
import inspect
import sys
import argparse
import time

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
sys.path.insert(0, pp)

from smsurvey import config


def get_dynamo(local=config.local):
    if local:
        return boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
    else:
        return boto3.client('dynamodb', region_name='us-east-1')


def create_cache(t_name, dynamo=None):

    if dynamo is None:
        dynamo = get_dynamo()

    t = dynamo.create_table(
        TableName=t_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'survey_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'time_rule_id',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'survey_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'time_rule_id',
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    while True:
        response = dynamo.describe_table(
            TableName=t_name
        )
        if response['Table']['TableStatus'] == 'ACTIVE':
            break
        else:
            print("Still creating")
            time.sleep(5)

    print("Cache status: ", t['TableDescription']['TableStatus'])


def create(force, local=config.local, test=False):
    dynamo = get_dynamo(local)

    t_name = config.time_rule_backend_name

    if test:
        t_name += "Test"

    if force:
        print("Creating " + t_name + " - FORCED")
        if t_name in dynamo.list_tables()['TableNames']:
            print("Removing old " + t_name)
            dynamo.delete_table(TableName=t_name)

            while t_name in dynamo.list_tables()['TableNames']:
                print("Still deleting")
                time.sleep(5)
    else:
        if t_name in dynamo.list_tables()['TableNames']:
            while True:
                answer = input(t_name + " already exists. Delete existing and create new? (Yes/n)")

                if answer == 'n':
                    exit(0)
                elif answer == 'Yes':
                    dynamo.delete_table(TableName=t_name)

                    while t_name in dynamo.list_tables()['TableNames']:
                        print("Still deleting")
                        time.sleep(5)

                    break

    print("Creating " + t_name)
    create_cache(t_name)
    print("Finished creating " + t_name)

    return t_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", action="store_true", dest="force")
    parser.add_argument("-l", action="store_true", dest="local")
    args = parser.parse_args()

    create(args.force, args.local)

