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
from smsurvey.core.model.survey.question import Question
from smsurvey.core.model.survey.survey_state_machine import SurveyState
from smsurvey.core.services.question_service import QuestionOperationException
from smsurvey.core.services.question_service import QuestionService
from smsurvey.utility_scripts import create_question_cache


class MockQuestion(Question):

    def __init__(self, question_identifier):
        self.question_identifier = question_identifier

    def ask_question(self):
        return self.question_identifier

    def process_response(self, response):
        return SurveyState.new_state_object(1, 1)


class TestQuestionService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)

        if 'QuestionTest' in dynamo.list_tables()['TableNames']:
            dynamo.delete_table(TableName='QuestionTest')

        create_question_cache.create_cache('QuestionTest')

    def test_insert_question(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        qid = "abcde"
        service.insert("1_1", MockQuestion(qid))
        question = service.get("1_1")
        self.assertTrue(question.ask_question() == qid)

    def test_insert_question_safe_mode_off(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        qid = "123"
        service.insert("1_2", MockQuestion(qid))
        question = service.get("1_2")
        self.assertTrue(question.ask_question() == qid)

    def test_insert_question_id_exists(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        service.insert("1_3", MockQuestion("1"))
        self.assertRaises(QuestionOperationException, service.insert, "1_3", MockQuestion("2"))

    def test_insert_question_id_exists_safe_mode_off(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        service.insert("1_4", MockQuestion("1"), False)
        service.insert("1_4", MockQuestion("2"), False)
        question = service.get("1_4")
        self.assertTrue(question.ask_question() == "2")

    def test_insert_question_invalid_id(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        self.assertRaises(QuestionOperationException, service.insert, "1.5", MockQuestion(""))

    def test_insert_question_invalid_id_safe_mode_off(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        self.assertRaises(QuestionOperationException, service.insert, "1.6", MockQuestion(""), False)

    def test_insert_question_not_question_object(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        self.assertRaises(QuestionOperationException, service.insert, "1_7", [])

    def test_insert_question_not_question_object_safe_mode_off(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        self.assertRaises(QuestionOperationException, service.insert, "1_8", [], False)

    def test_get_question(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        qid = "shouldgetthis"
        service.insert("2_1", MockQuestion(qid))
        question = service.get("2_1")
        self.assertTrue(question.ask_question() == qid)

    def test_get_question_incorrect_key(self):
        service = QuestionService(config.dynamo_url, 'QuestionTest')
        question = service.get("2_2")
        self.assertIsNone(question)
        
    @classmethod
    def tearDownClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)
        dynamo.delete_table(TableName='QuestionTest')
