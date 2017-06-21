import boto3

from smsurvey import config

dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)


def create_cache(cache_name):
    survey_cache = dynamo.create_table(
        TableName=cache_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'event_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'survey_instance_id',
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
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print("Cache status: ", survey_cache['TableDescription']['TableStatus'])


if __name__ == "__main__":
    if 'SurveyState' in dynamo.list_tables()['TableNames']:
        while True:
            answer = input("SurveyState already exists. Delete existing and create new? (Yes/n)")

            if answer == 'n':
                exit(0)
            elif answer == 'Yes':
                dynamo.delete_table(TableName='SurveyState')
                break

    create_cache('SurveyState')