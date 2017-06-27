import boto3
import time
import os

from botocore.exceptions import ClientError

from smsurvey import config
from smsurvey.core.security.secure import encrypt_password
from smsurvey.core.security.secure import SecurityException
from smsurvey.interface.services.owner_service import OwnerService


class PluginService:

    def __init__(self, cache_url, cache_name):
        self.dynamo = boto3.client('dynamodb', region_name='us_west_2', endpoint_url=cache_url)
        self.cache_name = cache_name

    def get_plugin(self, owner, plugin_id):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'plugin_id' : {
                        'S': plugin_id
                    },
                    'owner': {
                        'S': owner
                    }
                },
                ConsistentRead=True,
                ReturnConsumedCapacity="False"
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                item = response['Item']
                salt = item['salt']['B']
                token = item['token']['S']

                return {
                    'owner': owner,
                    'plugin_id': plugin_id,
                    'salt': salt,
                    'token': token
                }
            else:
                return None

    def validate_plugin(self, owner, plugin_id, token):
        plugin = self.get_plugin(owner, plugin_id)

        if plugin is not None:
            test = encrypt_password(token, plugin['salt']).decode()
            return test == plugin['token']
        else:
            return False

    def is_plugin_registered(self, owner, plugin_id):
        plugin = self.get_plugin(owner, plugin_id)

        return plugin is not None

    def register_plugin(self, owner, password, plugin_id):

        at = owner.find('@')

        if at == -1:
            raise SecurityException("Invalid owner, must be in format name@domain")

        if self.is_plugin_registered(owner, plugin_id):
            raise SecurityException("Plugin already registered to owner")

        name = owner[:at]
        domain = owner[at+1:]

        owner_service = OwnerService(config.dynamo_url, config.owner_backend_name)

        if owner_service.does_owner_exist(domain, name):
            if owner_service.validate_password(domain, name, password):
                salt = os.urandom(16)
                token = encrypt_password(owner + str(time.time()), salt).decode()
                salt2 = os.urandom(16)
                token2 = encrypt_password(token, salt2).decode()

                self.dynamo.put_item(
                    TableName=self.cache_name,
                    Item={
                        'owner': {
                            'S': owner
                        },
                        'plugin_id': {
                            'S': plugin_id
                        },
                        'token': {
                            'S': token2
                        },
                        'salt': {
                            'B': salt2
                        }
                    }
                )

                return token
            else:
                raise SecurityException("Unable to validate owner")
        else:
            raise SecurityException("Owner does not exist")
