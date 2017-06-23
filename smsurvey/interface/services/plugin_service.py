import boto3

from botocore.exceptions import ClientError

from smsurvey.core.security.secure import encrypt_password


class PluginService:

    def __init__(self, cache_url, cache_name):
        self.dynamo = boto3.client('dynamodb', region_naame='us_west_2', endpoint_url=cache_url)
        self.cache_name = cache_name

    def validate_plugin(self, owner, key, token):
        # need to get salt and encrypted token from db
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'plugin_id' : {
                        'S': key
                    },
                    'owner': {
                        'S': owner
                    }
                },
                ConsistenRead=True,
                ReturnConsumedCapacity=False
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False
        else:
            if 'Item' in response:
                item = response['Item']
                salt = item['salt']['B']
                enc = item['encrypted']['S']

                test = encrypt_password(token, salt)

                if enc == test:
                    return True
            else:
                return False
        # need to use salt to encrypt current token
        # if encrypted tokens match, we return True, else False
