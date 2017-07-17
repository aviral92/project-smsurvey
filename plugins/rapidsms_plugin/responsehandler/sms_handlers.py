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
        token = os.environ.get("SEC_TOKEN")
        owner = os.environ.get("OWNER")
        domain = os.environ.get("DOMAIN")
        plugin_id = os.environ.get("PLUGIN_ID")
        a = owner + "@" + domain + "-" + plugin_id + ":" + token
        url = os.environ.get("SYSTEM_URL")

        b64 = base64.b64encode(a.encode()).decode()
        headers = {
            "Authorization": "Basic " + b64
        }
        r = requests.get(url + "surveys", headers=headers)
        response = json.loads(r.text)

        for sid in response["ids"]:
            survey_id = sid[:1]

            if survey_id == text:
                SurveyStarter.start_survey(sid)

    def help(self):
        self.respond("Send START SURVEY_ID to start a survey batch")
