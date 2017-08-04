import os

import pymysql

from smsurvey.schedule.task import Task


class ScheduleService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD"), test=False):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password

        if test:
            self.database = "test"
        else:
            self.database = "dbase"

    def insert_task(self, survey_id, time_rule_id):
        sql = "INSERT INTO schedule (survey_id, time_rule_id) VALUES (%s, %s)"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (survey_id, time_rule_id))
                connection.commit()
                cursor.fetchall()
        finally:
            connection.close()

    def get_all_tasks(self):
        sql = "SELECT * FROM schedule"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
        finally:
            connection.close()

        arr = []

        for row in result:
            arr.append(Task.from_tuple(row))

        return arr
