import base64
import requests
import json

from rapidsms.apps.base import AppBase
from rapidsms.router import send, lookup_connections

class PingPong(AppBase):

    def handle(self, msg):
        if msg.text == 'ping':
            msg.respond('pong')
            return True
        return False


class SurveyStarter:

    @staticmethod
    def start_survey(survey_id):
        # make call to start survey
        data = {
            'action': 'start'
        }

        url = 'http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/'
        b64 = base64.b64encode("owner@test-12345"
                               ":a8ecc91c71df2d5a0220adf5982bd35c083d4dd6056027d5f4f1d60feb47455c21e714dc3a67fc0954ed478f5cacfb77e7035f287bf7168baa6926cb4e40897d".encode()).decode()
        headers = {
            "Authorization": "Basic " + b64
        }

        requests.post(url + 'surveys/' + survey_id, json.dumps(data), headers=headers)

        #get participant for survey
        participant = requests.get(url + "participants?survey_id=" + survey_id, headers=headers)
        participant_id = json.loads(participant.text)["participant_id"]

        #send first question to participant

        first_question = requests.get(url + 'surveys/' + survey_id + "/latest", headers=headers)
        question_text = json.loads(first_question.text)["question_text"]

        send(question_text, lookup_connections(backend="message_tester", identities=[participant_id]))

