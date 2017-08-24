import inspect
import os
import sys
import unittest

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
pppp = os.path.dirname(ppp)
ppppp = os.path.dirname(pppp)
sys.path.insert(0, ppppp)

from core.model.model import Question


class TestQuestion(unittest.TestCase):

    def test_question_free_input_any_response(self):
        expected = "true"
        question = Question("1", "", "", expected, free_input=True, final=False)
        actual = question.process("bob")
        self.assertEqual(expected, actual)

    def test_question_fixed_input_valid_response(self):
        expected = {
            '0': "true"
        }

        question = Question("1", "", "", expected, free_input=True, final=False)
        actual = question.process("0")
        self.assertEqual(expected, actual)

    def test_question_fixed_input_invalid_response(self):
        expected = {
            '0': "true"
        }

        question = Question("1", "", "", expected, free_input=False, final=False)
        actual = question.process("1")
        self.assertEqual(actual, 'INV_RESP')
