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

from core.model.model import ResponseSet


class TestResponseSet(unittest.TestCase):

    def test_add_response(self):
        response_set = ResponseSet('1', '1')
        response_set.add_response("variable_name", "1")

        self.assertTrue(response_set.response_dict['variable_name'] == "1")

    def test_get_response(self):
        response_set = ResponseSet('1', '1')
        response_set.add_response("variable_name", "1")
        actual = response_set.get_response("variable_name")

        self.assertEqual("1", actual)

    def test_get_response_none(self):
        response_set = ResponseSet('1', '1')
        self.assertIsNone(response_set.get_response("anything"))

    def test_to_json(self):
        response_set = ResponseSet('1', '1')
        response_set.add_response("variable_name", "1")
        actual = response_set.to_json()
        expected = '{"survey_id":"1","survey_instance_id":"1", "data":{"variable_name": "1"}}'
        self.assertEqual(expected, actual)