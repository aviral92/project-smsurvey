import unittest

import boto3
import os
import inspect
import sys

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
pppp = os.path.dirname(ppp)
ppppp = os.path.dirname(pppp)
sys.path.insert(0, ppppp)

from smsurvey import config
from smsurvey.core.model.survey.survey_state_machine import SurveyState, SurveyStateOperationException, SurveyStatus
from smsurvey.core.services.survey_state_service import SurveyStateService
from smsurvey.utility_scripts import create_survey_state_cache


class TestSurveyStateService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)

        if 'SurveyStateTest' in dynamo.list_tables()['TableNames']:
            dynamo.delete_table(TableName='SurveyStateTest')

        create_survey_state_cache.create_cache('SurveyStateTest')

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
        self.assertRaises(SurveyStateOperationException, service.insert, survey)

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
        self.assertRaises(SurveyStateOperationException, service.update, "3_4", survey)

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
        self.assertRaises(SurveyStateOperationException, service.update, "3_5", survey)

    def test_update_object_invalid_update_different_surveys(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 8)
        service.insert(survey)
        survey_received = service.get("3_8")
        survey_received.survey_instance_id = "wrong"
        self.assertRaises(SurveyStateOperationException, service.update, "3_8", survey_received)

    def test_update_object_invalid_update_different_versions(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 9)
        service.insert(survey)
        survey_received = service.get("3_9")
        survey_received.survey_state_version = 1337
        self.assertRaises(SurveyStateOperationException, service.update, "3_9", survey_received)

    def test_update_object_invalid_update_different_questions(self):
        service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')
        survey = SurveyState.new_state_object(3, 10)
        service.insert(survey)
        survey_received = service.get("3_10")
        survey_received.next_question = 1337
        self.assertRaises(SurveyStateOperationException, service.update, "3_9", survey_received)

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
        self.assertRaises(SurveyStateOperationException, service.delete, "4_4")

    @classmethod
    def tearDownClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)
        dynamo.delete_table(TableName='SurveyStateTest')
