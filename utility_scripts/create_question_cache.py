import boto3

from smsurvey import config

dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)


def create_cache(cache_name):
    question_cache = dynamo.create_table(
        TableName=cache_name,
        AttributeDefinitions=[
            {
                'AttributeName': 'question_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'survey_id',
                'AttributeType': 'S'
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'survey_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'question_id',
                'KeyType': 'RANGE'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print("Cache status: ", question_cache['TableDescription']['TableStatus'])

if __name__ == "__main__":
    if 'Question' in dynamo.list_tables()['TableNames']:
        while True:
            answer = input("Question already exists. Delete existing and create new? (Yes/n)")

            if answer == 'n':
                exit(0)
            elif answer == 'Yes':
                dynamo.delete_table(TableName='Question')
                break

    create_cache('Question')
