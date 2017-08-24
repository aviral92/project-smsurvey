import inspect
import os
import sys
import unittest

import boto3

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
pppp = os.path.dirname(ppp)
ppppp = os.path.dirname(pppp)
sys.path.insert(0, ppppp)

from smsurvey import config
from core.model.model.survey import SurveyState, SurveyStateOperationException, SurveyStatus


class TestSurveyStateService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)

        if 'SurveyStateTest' in dynamo.list_tables()['TableNames']:
            dynamo.delete_table(TableName='SurveyStateTest')

        create_survey_state_cache.create_cache('SurveyStateTest')
        cls.service = SurveyStateService(config.dynamo_url, 'SurveyStateTest')

    def test_insert_new_survey_state(self):
        survey = SurveyState.new_state_object("1", "test", "1")
        self.service.insert(survey)
        survey_received = self.service.get("1", "1")
        self.assertTrue(survey == survey_received)

    def test_insert_new_survey_state_safe_mode_off(self):
        survey = SurveyState.new_state_object("1", "test", "2")
        self.service.insert(survey, False)
        survey_received = self.service.get("1", "2")
        self.assertTrue(survey == survey_received)

    def test_insert_new_survey_state_safe_mode_off_key_exists(self):
        survey = SurveyState.new_state_object("1", "test", "3")
        self.service.insert(survey, False)
        survey_received = self.service.get("1", "3")
        self.assertTrue(survey == survey_received)

    def test_insert_new_survey_key_exists(self):
        survey = SurveyState.new_state_object("1", "test", "4")
        self.service.insert(survey)
        self.assertRaises(SurveyStateOperationException, self.service.insert, survey)

    def test_get_object_exists(self):
        survey = SurveyState.new_state_object("2", "test", "1")
        self.service.insert(survey)
        survey_received = self.service.get("2", "1")
        self.assertTrue(survey == survey_received)

    def test_get_object_does_not_exist(self):
        survey_received = self.service.get("2", "1")
        self.assertIsNone(survey_received)

    def test_update_object(self):
        survey = SurveyState.new_state_object("3", "test", "1")
        self.service.insert(survey)
        survey_received = self.service.get("3", "1")
        survey_received.survey_status = SurveyStatus.TERMINATED_COMPLETE
        self.service.update(survey_received)
        survey_received = self.service.get("3", "1")
        self.assertTrue(survey_received.survey_status == SurveyStatus.TERMINATED_COMPLETE)

    def test_update_object_invalid_update_different_versions(self):
        survey = SurveyState.new_state_object("3", "test", "9")
        self.service.insert(survey)
        survey_received = self.service.get("3", "9")
        survey_received.survey_state_version = 1337
        self.assertRaises(SurveyStateOperationException, self.service.update, survey_received)

    def test_delete_object(self):
        survey = SurveyState.new_state_object(4, "test", "1")
        self.service.insert(survey)
        survey_received = self.service.get("4", "1")
        self.assertTrue(survey == survey_received)
        self.service.delete("4_1")
        survey_received = self.service.get("4", "1")
        self.assertIsNone(survey_received)

    def test_delete_object_key_not_exist(self):
        self.service.delete("4_3")

    @classmethod
    def tearDownClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)
        dynamo.delete_table(TableName='SurveyStateTest')
