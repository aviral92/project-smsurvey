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
from core.model.model import Question
from smsurvey.core.services.question_service import QuestionOperationException
from smsurvey.core.services.question_service import QuestionService
from smsurvey.utility_scripts import create_question_store


class TestQuestionService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)

        if 'QuestionTest' in dynamo.list_tables()['TableNames']:
            dynamo.delete_table(TableName='QuestionTest')

        create_question_store.create_cache('QuestionTest')
        cls.service = QuestionService(config.dynamo_url, 'QuestionTest')

    def test_insert_question(self):
        qid = "abcde"
        question = Question("1", qid, "", None)

        self.service.insert("1_1", question)
        question = self.service.get("1_1")
        self.assertTrue(question.question_text == qid)

    def test_insert_question_safe_mode_off(self):
        qid = "123"
        question = Question("1", qid, "", None)

        self.service.insert("1_2", question)
        question = self.service.get("1_2")
        self.assertTrue(question.question_text == qid)

    def test_insert_question_id_exists(self):
        question1 = Question("1", "1", "", None)
        question2 = Question("1", "2", "", None)
        self.service.insert("1_3", question1)
        self.assertRaises(QuestionOperationException, self.service.insert, "1_3", question2)

    def test_insert_question_id_exists_safe_mode_off(self):
        question1 = Question("1", "1", "", None)
        question2 = Question("1", "2", "", None)
        self.service.insert("1_4", question1, False)
        self.service.insert("1_4", question2, False)
        question = self.service.get("1_4")
        self.assertTrue(question.question_text == "2")

    def test_insert_question_invalid_id(self):
        question = Question("1", "", "", None)
        self.assertRaises(QuestionOperationException, self.service.insert, "1.5", question)

    def test_insert_question_invalid_id_safe_mode_off(self):
        question = Question("1", "", "", None)
        self.assertRaises(QuestionOperationException, self.service.insert, "1.6", question, False)

    def test_insert_question_not_question_object(self):
        self.assertRaises(QuestionOperationException, self.service.insert, "1_7", [])

    def test_insert_question_not_question_object_safe_mode_off(self):
        self.assertRaises(QuestionOperationException, self.service.insert, "1_8", [], False)

    def test_get_question(self):
        qid = "shouldgetthis"
        question = Question("1", qid, "", None)
        self.service.insert("2_1", question)
        question = self.service.get("2_1")
        self.assertTrue(question.question_text == qid)

    def test_get_question_incorrect_key(self):
        question = self.service.get("2_2")
        self.assertIsNone(question)
        
    @classmethod
    def tearDownClass(cls):
        dynamo = boto3.client('dynamodb', region_name='us-west-2', endpoint_url=config.dynamo_url)
        dynamo.delete_table(TableName='QuestionTest')
