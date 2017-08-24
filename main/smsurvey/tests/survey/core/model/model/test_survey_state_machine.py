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

from core.model.model.survey import SurveyState
from core.model.model.survey import SurveyStatus


class TestSurveyState(unittest.TestCase):

    def test_eq(self):
        one = SurveyState.new_state_object("1", "1", "1")
        two = SurveyState.new_state_object("2", "1", "1")
        self.assertNotEqual(one, two)

        three = SurveyState.new_state_object("1", "1", "1")
        four = SurveyState.new_state_object("1", "1", "1")
        four.event_id = '2'
        self.assertNotEqual(three, four)

        five = SurveyState.new_state_object("1", "2", "1")
        six = SurveyState.new_state_object("1", "4", "1")
        self.assertNotEqual(five, six)

        seven = SurveyState.new_state_object("1", "1", "1")
        eight = SurveyState.new_state_object("1", "1", "1")
        eight.survey_status = SurveyStatus.CREATED_MID
        self.assertNotEqual(seven, eight)

        nine = SurveyState.new_state_object("1", "1", "1")
        ten = SurveyState.new_state_object("1", "1", "1")
        ten.priority = 4
        self.assertNotEqual(nine, ten)

        eleven = SurveyState.new_state_object("1", "1", "1")
        twelve = SurveyState.new_state_object("1", "1", "1")
        twelve.timestamp = 1
        self.assertNotEqual(eleven, twelve)

        thirteen = SurveyState.new_state_object("1", "1", "1")
        fourteen = SurveyState.new_state_object("1", "1", "1")
        fourteen.timeout = 1
        self.assertNotEqual(thirteen, fourteen)

        fifteen = SurveyState.new_state_object("1", "1", "1")
        sixteen = SurveyState.new_state_object("1", "1", "1")
        sixteen.survey_state_version = -1
        self.assertNotEqual(fifteen, sixteen)
