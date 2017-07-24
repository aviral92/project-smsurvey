import boto3

from botocore.exceptions import ClientError

from smsurvey import config
from smsurvey.core.schedule.time_rule.time_rule import *


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
                    'survey_id': {'S': survey_id},
                    'time_rule_id': {'S': time_rule_id}
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
        else:
            if 'Item' in response:
                tr_type = response['Item']['type']['S']

                if tr_type == 'no_repeat':
                    return NoRepeatTimeRule.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat_daily':
                    return RepeatsDailyTimeRule.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat_monthly_date':
                    return RepeatsMonthlyDate.from_params(response['Item']['params']['S'])

                if tr_type == 'repeat_monthly_day':
                    return RepeatsMonthlyDay.from_params(response['Item']['params']['S'])

                if tr_type == 'repeats_weekly':
                    return RepeatsWeekly.from_params(response['Item']['params']['S'])

        return None
