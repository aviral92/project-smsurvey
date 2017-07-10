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
                               ":a8ecc91c71df2d5a0220adf5982bd35c083d4dd6056027d5f4f1d60feb47455c21e714dc3a67fc0954ed478f5cacfb77e7035f287bf7168baa6926cb4e40897d".encode()).decode()
        headers = {
            "Authorization": "Basic " + b64
        }
        r = requests.get(url, headers=headers)
        response = json.loads(r.text)

        for id in response["ids"]:
            survey_id = id[:1]

            if survey_id == text:
                SurveyStarter.start_survey(survey_id)
                self.respond(survey_id)


        #self.respond(response["ids"])



    def help(self):
        self.respond("Send START SURVEY_ID to start a survey batch")
