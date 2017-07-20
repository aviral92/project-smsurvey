import os
import pymysql

from smsurvey.core.model.survey.protocol import Protocol


class ProtocolService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD")):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password
        self.database = "dbase"

    def get(self, protocol_id):
        sql = "SELECT * from survey WHERE survey_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, protocol_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            survey_tuple = result[0]
            return Protocol.from_tuple(survey_tuple)

        return None

    def create_protocol(self, first_question):
        sql = "INSERT INTO survey (protocol_id) VALUES(%s)"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, first_question)
                connection.commit()
                connection.fetchall()
                protocol_id = cursor.lastrowid
        finally:
            connection.close()

        return Protocol(protocol_id, first_question)