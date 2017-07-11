import requests
import base64
import json

from rapidsms.contrib.handlers import KeywordHandler
from .app import SurveyStarter

### This is all temporary


class SurveyStartHandler(KeywordHandler):

    keyword = "START"

    def handle(self, text):
        url = 'http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/surveys'
        b64 = base64.b64encode("owner@test-12345"
                               ":f7ddea7c7cb264d12d1d4e5f9dd0221529487b5331748ba96d6e088fdc87cf314b1caa5359366bbb6ab757d4d2ba17b969a541f0d6a3edc837c5c93558074f26".encode()).decode()
        headers = {
            "Authorization": "Basic " + b64
        }
        r = requests.get(url, headers=headers)
        response = json.loads(r.text)

        for sid in response["ids"]:
            survey_id = sid[:1]

            if survey_id == text:
                SurveyStarter.start_survey(sid)

    def help(self):
        self.respond("Send START SURVEY_ID to start a survey batch")
