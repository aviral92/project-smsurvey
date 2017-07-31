import os
import pymysql

from smsurvey.core.model.survey.state import State, StateException


class StateService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD")):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password
        self.database = "dbase"

    def get_state(self, state_id):
        sql = "SELECT * from state_version0 WHERE state_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, state_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            survey_tuple = result[0]
            return State.from_tuple(survey_tuple)

        return None

    def create_state(self, instance_id, question_id, status, priority):
        sql = "INSERT INTO state_version0 (instance_id, question_id, status, priority) VALUES(%s,%s,%s,%s)"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (instance_id, question_id, status.value, priority))
                connection.commit()
                cursor.fetchall()
                state_id = cursor.lastrowid
        finally:
            connection.close()

        return State(state_id, instance_id, question_id, status, priority)

    def update_state(self, state):
        existing = self.get_state(state.state_id)

        if existing is None:
            raise StateException("Attempting update state that does not exist")

        if existing.question_id != state.question_id:
            raise StateException("Cannot modify question id")
        if existing.instance_id != state.instance_id:
            raise StateException("Cannot modify instance id")

        sql = "UPDATE state_version0 SET status = %s, priority = %s WHERE state_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (state.status.value, state.priority, state.state_id))
                connection.commit()
        finally:
            connection.close()

    def delete_state(self, state):
        if self.get_state(state.state_id) is not None:
            sql = "DELETE FROM state_version0 WHERE state_id = %s"

            connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                         host=self.database_url, database=self.database, charset="utf8")

            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql, state.state_id)
                    connection.commit()
            finally:
                connection.close()

    def delete_states_for_instances(self, instance_ids):
        print("Deleting states for instances " + str(instance_ids))
        sql = "DELETE FROM state_version0 WHERE instance_id IN %s"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [instance_ids])
                connection.commit()
        finally:
            connection.close()

    def get_next_state_in_instance(self, instance_id, status="*"):

        if status == "*":
            sql = "SELECT * FROM state_version0 WHERE instance_id = %s"
        else:
            sql = "SELECT * FROM state_version0 WHERE instance_id = %s AND status = %s"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                if status == "*":
                    cursor.execute(sql, instance_id)
                else:
                    cursor.execute(sql, (instance_id, status.value))
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            lowest_priority = result[0][4]
            lowest_state = result[0]

            for state_tuple in result:
                priority = state_tuple[4]
                if priority < lowest_priority:
                    lowest_priority = priority
                    lowest_state = state_tuple

            return State.from_tuple(lowest_state)

        return None

    def get_state_by_instance_and_question(self, instance_id, question_id):
        sql = "SELECT * FROM state_version0 WHERE instance_id = %s AND question_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (instance_id, question_id))
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            state_tuple = result[0]
            return State.from_tuple(state_tuple)

    def get_unfinished_states(self, instance_id):
        sql = "SELECT * FROM state_version0 WHERE instance_id = %s AND status < 500"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, instance_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        states = []

        for state_tuple in result:
            states.append(State.from_tuple(state_tuple))

        return states
