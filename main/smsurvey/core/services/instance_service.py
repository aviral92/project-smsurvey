import os
import pymysql

from smsurvey.core.model.survey.instance import Instance
from smsurvey.core.services.owner_service import OwnerService

class InstanceService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD")):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password
        self.database = "dbase"

    def get_instance(self, instance_id):
        sql = "SELECT * from instance WHERE instance_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, instance_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            survey_tuple = result[0]
            return Instance.from_tuple(survey_tuple)

        return None

    def create_instance(self, survey_id, timeout):
        sql = "INSERT INTO instance (survey_id, timeout) VALUES(%s, %s)"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (survey_id, timeout))
                connection.commit()
                protocol_id = cursor.lastrowid
        finally:
            connection.close()

        return self.get_instance(protocol_id)

    def get_owner(self, instance_id):
        sql = "SELECT owner_name, owner_domain FROM instance INNER JOIN survey ON" \
              " instance.survey_id = survey.survey_id WHERE instance_id = %s"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, instance_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            return OwnerService().get(result[0][0], result[0][1])

        return None

    def get_by_owner(self, owner_name, owner_domain, survey_id):
        sql = "SELECT instance_id FROM instance INNER JOIN survey ON instance.survey_id = survey.survey_id WHERE" \
              " owner_name = %s AND owner_domain = %s AND survey.survey_id = %s"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (owner_name, owner_domain, survey_id))
                result = cursor.fetchall()
        finally:
            connection.close()

        answer = []
        for instance_tuple in result:
            answer.append(instance_tuple[0])

        return answer

    def get_survey_id(self, instance_id):
        instance = self.get_instance(instance_id)

        if instance is not None:
            return instance.survey_id

        return None

