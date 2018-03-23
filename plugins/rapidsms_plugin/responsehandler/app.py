import base64
import requests
import json

from rapidsms.router import send, lookup_connections
from rapidsms.apps.base import AppBase

from responsehandler.models import ParticipantModel, OwnerModel


class ResponseRespond(AppBase):

    def handle(self, msg):
        p = msg.connection.identity
        print("Contact Number:", p)
        participant = ParticipantModel.objects.get(phone_number=p)
        instance_id = str(participant.instance_id)
        owner_id = participant.owner_id

        owner = OwnerModel.objects.get(owner_id=owner_id)
        url = str(owner.url)
        token = str(owner.token)
        plugin_id = str(owner.plugin_id)
        owner_id = str(owner_id)

        a = owner_id + "-" + plugin_id + ":" + token
        b64 = base64.b64encode(a.encode()).decode()

        headers = {
            "Authorization": "Basic " + b64
        }

        data = {
            "response": msg.text,
            "contact": p
        }

        r = requests.post(url + '/instances/' + instance_id + "/latest", data=json.dumps(data), headers=headers)
        rd = json.loads(r.text)
        if rd['status'].lower() == 'success':
            if rd['response_accepted'].lower() == 'true':
                new_question = requests.get(url + '/instances/' + instance_id + "/latest", data=json.dumps(data),
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
    def start_survey(plugin_id, owner_id, token, url, survey_id, instance_id):
        # make call to start survey
        print("Parameters::", plugin_id, owner_id, token, url, survey_id, instance_id)
        data = {
            'action': 'start'
        }

        a = owner_id + "-" + plugin_id + ":" + token
        b64 = base64.b64encode(a.encode()).decode()

        headers = {
            "Authorization": "Basic " + b64
        }

        requests.post(url + '/instances/' + str(instance_id), json.dumps(data), headers=headers)

        #get participant for survey
        params = "?survey_id=" + str(survey_id) + "&instance_id=" + str(instance_id)
        participant_request = requests.get(url + "/participants" + params, headers=headers)
        participant = json.loads(participant_request.text)
        participant_number = participant["participant"]

        p = ParticipantModel.objects.filter(phone_number=participant_number).first()

        if p is not None:
            p.delete()

        p = ParticipantModel(instance_id=instance_id, phone_number=participant_number, owner_id=int(owner_id))
        p.save()

        first_question = requests.get(url + '/instances/' + str(instance_id) + "/latest", headers=headers)
        question_text = json.loads(first_question.text)["question_text"]

        send(question_text, lookup_connections(backend="twilio-backend", identities=[participant_number]))

