import boto3

from datetime import datetime

from botocore.exceptions import ClientError

from smsurvey.schedule.time_rule.time_rule import NoRepeat, RepeatsDaily, RepeatsMonthlyDate, \
    RepeatsMonthlyDay, RepeatsWeekly

from smsurvey import config


class TimeRuleService:

    def __init__(self, cache_name=config.time_rule_backend_name, local=config.local):
        if local:
            self.dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url_local)
        else:
            self.dynamo = boto3.client('dynamodb', region_name='us-east-1')

        self.cache_name = cache_name

    def get(self, survey_id, time_rule_id):
        try:
            response = self.dynamo.get_item(
                TableName=self.cache_name,
                Key={
                    'survey_id': {'S': str(survey_id)},
                    'time_rule_id': {'S': str(time_rule_id)}
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                tr_type = response['Item']['type']['S']

                if tr_type == 'no-repeat':
                    return NoRepeat.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat-daily':
                    return RepeatsDaily.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat-monthly-date':
                    return RepeatsMonthlyDate.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat-monthly-day':
                    return RepeatsMonthlyDay.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat-weekly':
                    return RepeatsWeekly.from_params(response['Item']['params']['S'])

        return None

    def insert(self, survey_id, time_rule, time_rule_id=str(datetime.now())):
        params = time_rule.to_params

        self.dynamo.put_item(
            TableName=self.cache_name,
            Item={
                'survey_id': {
                    'S': str(survey_id)
                },
                'time_rule_id': {
                    'S': str(time_rule_id)
                },
                'type': {
                    'S': str(time_rule.get_type())
                },
                'params': {
                    'S': str(params)
                }
            }
        )
        return time_rule_id
