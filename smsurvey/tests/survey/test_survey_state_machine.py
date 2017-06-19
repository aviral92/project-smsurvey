import unittest
import boto3

import smsurvey.config as config

from smsurvey.survey.survey_state_machine import SurveyCacheOperationException
from smsurvey.survey.survey_state_machine import SurveyState
from smsurvey.survey.survey_state_machine import SurveyStateService
from smsurvey.survey.survey_state_machine import SurveyStatus


class TestSurveyStateService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)

        if 'SurveyStateTest' in dynamo.list_tables()['TableNames']:
            dynamo.delete_table(TableName='SurveyStateTest')

        dynamo.create_table(
            TableName='SurveyStateTest',
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

    def test_insert_new_survey_state(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(1, 1)
        service.insert(survey)
        survey_received = service.get("1_1")
        self.assertTrue(survey == survey_received)

    def test_insert_new_survey_state_safe_mode_off(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(1, 2)
        service.insert(survey, False)
        survey_received = service.get("1_2")
        self.assertTrue(survey == survey_received)

    def test_insert_new_survey_state_safe_mode_off_key_exists(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(1, 2)
        service.insert(survey, False)
        survey_received = service.get("1_2")
        self.assertTrue(survey == survey_received)

    def test_insert_new_survey_state_safe_mode_on_key_exists(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(1, 2)
        self.assertRaises(SurveyCacheOperationException, service.insert, survey)

    def test_get_object_exists(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(2, 1)
        service.insert(survey)
        survey_received = service.get("2_1")
        self.assertTrue(survey == survey_received)

    def test_get_object_does_not_exist(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey_received = service.get("2_1")
        self.assertIsNone(survey_received)

    def test_update_object(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 1)
        service.insert(survey)
        survey_received = service.get("3_1")
        survey_received.survey_status = SurveyStatus.TERMINATED_COMPLETE
        service.update("3_1", survey_received)
        survey_received = service.get("3_1")
        self.assertTrue(survey_received.survey_status == SurveyStatus.TERMINATED_COMPLETE)

    def test_update_object_safe_mode_off(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 2)
        service.insert(survey)
        survey_received = service.get("3_2")
        survey_received.survey_status = SurveyStatus.TERMINATED_COMPLETE
        service.update("3_1", survey_received, False)
        survey_received = service.get("3_2")
        self.assertTrue(survey_received.survey_status == SurveyStatus.TERMINATED_COMPLETE)

    def test_update_object_safe_mode_off_key_not_exist(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 3)
        survey.survey_status = SurveyStatus.TERMINATED_COMPLETE
        service.update("3_3", survey, False)
        survey_received = service.get("3_3")
        self.assertTrue(survey == survey_received)

    def test_update_object_safe_mode_on_key_not_exist(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 4)
        self.assertRaises(SurveyCacheOperationException, service.update, "3_4", survey)

    def test_update_object_safe_mode_off_key_does_not_match(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 5)
        service.insert(survey)
        survey.survey_status = SurveyStatus.TERMINATED_COMPLETE
        service.update("3_1", survey, False)
        survey_received = service.get("3_5")
        self.assertTrue(survey == survey_received)
        survey_received = service.get("3_1")
        self.assertTrue(survey != survey_received)

    def test_update_object_safe_mode_on_key_does_not_match(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 6)
        service.insert(survey)
        survey = SurveyState.new_state_object(3, 7)
        self.assertRaises(SurveyCacheOperationException, service.update, "3_5", survey)

    def test_update_object_invalid_update_different_surveys(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 8)
        service.insert(survey)
        survey_received = service.get("3_8")
        survey_received.survey_id = "wrong"
        self.assertRaises(SurveyCacheOperationException, service.update, "3_8", survey_received)

    def test_update_object_invalid_update_different_versions(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 9)
        service.insert(survey)
        survey_received = service.get("3_9")
        survey_received.survey_state_version = 1337
        self.assertRaises(SurveyCacheOperationException, service.update, "3_9", survey_received)

    def test_update_object_invalid_update_different_questions(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 10)
        service.insert(survey)
        survey_received = service.get("3_10")
        survey_received.next_question = 1337
        self.assertRaises(SurveyCacheOperationException, service.update, "3_9", survey_received)

    def test_delete_object(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(4, 1)
        service.insert(survey)
        survey_received = service.get("4_1")
        self.assertTrue(survey == survey_received)
        service.delete("4_1")
        survey_received = service.get("4_1")
        self.assertIsNone(survey_received)

    def test_delete_object_safe_mode_off(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(4, 2)
        service.insert(survey)
        survey_received = service.get("4_2")
        self.assertTrue(survey == survey_received)
        service.delete("4_2", False)
        survey_received = service.get("4_2")
        self.assertIsNone(survey_received)

    def test_delete_object_safe_mode_off_key_not_exist(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        service.delete("4_3", False)

    def test_delete_object_safe_mode_on_key_not_exist(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        self.assertRaises(SurveyCacheOperationException, service.delete, "4_4")

    @classmethod
    def tearDownClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)
        dynamo.delete_table(TableName='SurveyStateTest')
