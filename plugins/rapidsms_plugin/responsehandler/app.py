import base64
import requests
import json
import os

from rapidsms.router import send, lookup_connections
from rapidsms.apps.base import AppBase

from plugins.rapidsms_plugin.responsehandler.models import Participant

token = os.environ.get("SEC_TOKEN")
owner = os.environ.get("OWNER_NAME")
domain = os.environ.get("OWNER_DOMAIN")
plugin_id = os.environ.get("PLUGIN_ID")
a = owner + "@" + domain + "-" + plugin_id + ":" + token
url = os.environ.get("SYSTEM_URL")
b64 = base64.b64encode(a.encode()).decode()

headers = {
    "Authorization": "Basic " + b64
}



class ResponseRespond(AppBase):

    def handle(self, msg):
        p = msg.connection.identity

        instance_id = Participant.objects.get(phone_number=p)

        data = {
            "response": msg.text
        }

        r = requests.post(url + 'instances/' + instance_id + "/latest", data=json.dumps(data), headers=headers)
        rd = json.loads(r.text)

        if rd['status'].lower() == 'success':
            if rd['response_accepted'].lower() == 'true':
                new_question = requests.get(url + 'instances/' + instance_id + "/latest", data=json.dumps(data),
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
    def start_survey(survey_id, instance_id):
        # make call to start survey
        data = {
            'action': 'start'
        }

        requests.post(url + 'instances/' + str(instance_id), json.dumps(data), headers=headers)

        #get participant for survey
        participant_request = requests.get(url + "participants?survey_id=" + str(survey_id), headers=headers)
        participant = json.loads(participant_request.text)
        participant_number = participant["participant"]

        p = Participant(instance_id=instance_id, phone_number=participant_number)
        p.save()
        print(participant_number + " assigned to survey " + survey_id)

        first_question = requests.get(url + 'instances/' + str(instance_id) + "/latest", headers=headers)
        question_text = json.loads(first_question.text)["question_text"]

        send(question_text, lookup_connections(backend="twilio-backend", identities=[participant_number]))

