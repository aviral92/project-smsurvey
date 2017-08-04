import os
import pymysql

from smsurvey.core.model.survey.survey import Survey
from smsurvey.core.services.owner_service import OwnerService


class SurveyService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD"), test=False):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password

        if test:
            self.database = "test"
        else:
            self.database = "dbase"

    def get_survey(self, survey_id):
        sql = "SELECT * from survey WHERE survey_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, survey_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            survey_tuple = result[0]
            return Survey.from_tuple(survey_tuple)

        return None

    def insert(self, survey):
        sql = "INSERT INTO survey VALUES(%s, %s, %s, %s, %s)"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (survey.survey_id, survey.protocol_id, survey.participant_id, survey.owner_name,
                                     survey.owner_domain))
                connection.commit()
                cursor.fetchall()
        finally:
            connection.close()

    def get_owner(self, survey_id):
        survey = self.get_survey(survey_id)

        if survey is not None:
            return OwnerService().get(survey.owner_name, survey.owner_domain)
        pass
