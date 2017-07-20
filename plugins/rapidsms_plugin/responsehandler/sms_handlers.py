import requests
import base64
import json
import os

from rapidsms.contrib.handlers import KeywordHandler
from .app import SurveyStarter


class SurveyStartHandler(KeywordHandler):

    keyword = "START"

    def handle(self, text):
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
        r = requests.get(url + "instances?survey_id=" + text, headers=headers)
        response = json.loads(r.text)

        for iid in response["ids"]:
            SurveyStarter.start_survey(text, iid)

    def help(self):
        self.respond("Send START SURVEY_ID to start a survey batch")
