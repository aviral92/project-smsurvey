import boto3

dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8888")

if 'SurveyState' in dynamo.list_tables()['TableNames']:
    while True:
        answer = input("SurveyState already exists. Delete existing and create new? (Yes/n)")

        if answer == 'n':
            exit(0)
        elif answer == 'Yes':
            dynamo.delete_table(TableName='SurveyState')
            break


survey_cache = dynamo.create_table(
    TableName='SurveyState',
    AttributeDefinitions=[
        {
            'AttributeName': 'event_id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'survey_id',
            'AttributeType': 'S'
        }
    ],
    KeySchema=[
        {
            'AttributeName': 'event_id',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'survey_id',
            'KeyType': 'RANGE'
        }
    ],
    GlobalSecondaryIndexes=[
        {
            'IndexName': 'survey_id_index',
            'KeySchema': [
                {
                    'AttributeName': 'survey_id',
                    'KeyType': 'HASH'
                }
            ],
            'Projection': {
                'ProjectionType': 'KEYS_ONLY'
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