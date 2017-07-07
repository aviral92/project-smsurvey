import unittest
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

from smsurvey.core.model.survey.survey import Survey


class TestResponseSet(unittest.TestCase):
    def test_from_item(self):
        survey_id = {'S': "1"}
        instance_id = {'S': '2'}
        participant = {'S': '3'}

        item = {'survey_id': survey_id, 'instance_id': instance_id, 'participant': participant}
        survey = Survey.from_item(item)

        self.assertEqual(survey.survey_id, "1")
        self.assertEqual(survey.survey_instance_id, '2')
        self.assertEqual(survey.participant, '3')

