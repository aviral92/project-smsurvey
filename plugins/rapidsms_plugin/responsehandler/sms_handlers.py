import requests
import base64
import json
import os

from rapidsms.contrib.handlers import KeywordHandler
from .app import SurveyStarter

### This is all temporary


class SurveyStartHandler(KeywordHandler):

    keyword = "START"

    def handle(self, text):
        token = os.environ.get("plugin_token")
        a = "owner@test-12345:" + token
        url = 'http://project-smsurvey-lb-1432717712.us-east-1.elb.amazonaws.com/'
        b64 = base64.b64encode(a.encode()).decode()
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
