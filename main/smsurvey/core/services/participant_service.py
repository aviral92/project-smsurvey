import os
import pymysql

from smsurvey.core.model.survey.participant import Participant, ParticipantException


class ParticipantService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD")):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password
        self.database = "dbase"

    def get_participant(self, participant_id):
        sql = "SELECT * from participant WHERE participant_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, participant_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            participant_tuple = result[0]
            return Participant.from_tuple(participant_tuple)

        return None

    def is_participant_registered(self, participant_id):
        return self.get_participant(participant_id) is not None

    def register_participant(self, participant_id, participant_scratch):
        if self.is_participant_registered(participant_id):
            raise ParticipantException("Not unique participant_id")

        sql = "INSERT INTO participant VALUES(%s, %s)"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (participant_id, participant_scratch))
                connection.commit()
                connection.fetchall()
        finally:
            connection.close()
