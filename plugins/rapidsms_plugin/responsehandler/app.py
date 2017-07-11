import base64
import requests
import json

from rapidsms.router import send, lookup_connections
from rapidsms.apps.base import AppBase

url = 'http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/'
b64 = base64.b64encode("owner@test-12345"
                               ":f7ddea7c7cb264d12d1d4e5f9dd0221529487b5331748ba96d6e088fdc87cf314b1caa5359366bbb6ab757d4d2ba17b969a541f0d6a3edc837c5c93558074f26".encode()).decode()
headers = {
    "Authorization": "Basic " + b64
}

participant_lookup = {}


class ResponseRespond(AppBase):

    def handle(self, msg):
        p = msg.connection.identity
        survey_id = participant_lookup[p]
        # POST /surveys/[survey-id]/latest

        data = {
            "response": msg.text
        }

        r = requests.post(url + 'surveys/' + survey_id + "/latest", data=json.dumps(data), headers=headers)
        rd = json.loads(r.text)

        if rd['status'].lower() == 'success':
            if rd['response_accepted'].lower() == 'true':
                new_question = requests.get(url + 'surveys/' + survey_id + "/latest", data=json.dumps(data),
                                            headers=headers)

                if new_question.status_code == 200:
                    new_question_dic = json.loads(new_question.text)
                    msg.respond(new_question_dic['question_text'])

            else:
                if rd['reason'] == 'Survey has finished':
                    msg.respond("Answer not accepted as survey has been completed")
                else:
                    msg.respond(rd['pass_along_message'])

        return True


class SurveyStarter:

    @staticmethod
    def start_survey(survey_id):
        # make call to start survey
        data = {
            'action': 'start'
        }

        requests.post(url + 'surveys/' + survey_id, json.dumps(data), headers=headers)

        #get participant for survey
        participant_request = requests.get(url + "participants?survey_id=" + survey_id, headers=headers)
        participant = json.loads(participant_request.text)
        participant_number = participant["participant"]
        print(participant_number + " assigned to survey " + survey_id)

        participant_lookup[participant_number] = survey_id

        #send first question to participant

        first_question = requests.get(url + 'surveys/' + survey_id + "/latest", headers=headers)
        question_text = json.loads(first_question.text)["question_text"]

        send(question_text, lookup_connections(backend="twilio-backend", identities=[participant_number]))

