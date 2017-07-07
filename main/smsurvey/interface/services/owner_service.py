import boto3
import os

import smsurvey.core.security.secure as secure

from botocore.exceptions import ClientError

from smsurvey import config
from smsurvey.core.security.secure import SecurityException


class OwnerService:

    def __init__(self, cache_name=config.owner_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def get(self, domain, name):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'domain': {"S": domain},
                    'name': {"S": name}
                },
                ConsistentRead=True,
                ReturnConsumedCapacity="NONE"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                item = response['Item']
                salt = item['salt']['B']
                enc = item['password']['S']

                return {
                    'domain': domain,
                    'name': name,
                    'salt': salt,
                    'password': enc
                }
            else:
                return None

    def create_owner(self, domain, name, password):
        if self.does_owner_exist(domain, name):
            raise SecurityException("Owner already exists")

        salt = os.urandom(16)
        enc_password = secure.encrypt_password(password, salt).decode()

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'domain': {
                    'S': domain
                },
                'name': {
                    'S': name
                },
                'password': {
                    'S': enc_password
                },
                'salt': {
                    'B': salt
                }
            }
        )

    def does_owner_exist(self, domain, name):
        return self.get(domain, name) is not None

    def validate_password(self, domain, name, password):
        owner = self.get(domain, name)

        if owner is not None:
            print("owner found")
            test = secure.encrypt_password(password, owner['salt']).decode()
            return test == owner['password']
        else:
            return False
