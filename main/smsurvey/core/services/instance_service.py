import os
import pymysql
import time

from smsurvey.core.model.survey.instance import Instance
from smsurvey.core.model.survey.state import Status
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.services.state_service import StateService
from smsurvey.core.services.survey_service import SurveyService
from smsurvey.core.services.protocol_service import ProtocolService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.plugin_service import PluginService


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
            instance_tuple = result[0]
            return Instance.from_tuple(instance_tuple)

        return None

    def create_instance(self, survey_id):
        sql = "INSERT INTO instance (survey_id) VALUES(%s)"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, survey_id)
                connection.commit()
                protocol_id = cursor.lastrowid
        finally:
            connection.close()

        return self.get_instance(protocol_id)

    def delete_instances(self, instance_ids):
        print("Deleting instances " + str(instance_ids))

        sql = "DELETE FROM instance WHERE instance_id IN %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [instance_ids])
                connection.commit()
        finally:
            connection.close()

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

    def get_by_owner(self, owner_name, owner_domain, survey_id=None, status=None):
        if survey_id is None:
            sql = "SELECT instance_id FROM instance INNER JOIN survey ON instance.survey_id = survey.survey_id WHERE" \
              " owner_name = %s AND owner_domain = %s"
        else:
            sql = "SELECT instance_id FROM instance INNER JOIN survey ON instance.survey_id = survey.survey_id WHERE" \
                  " owner_name = %s AND owner_domain = %s AND survey.survey_id = %s"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                if survey_id is None:
                    cursor.execute(sql, (owner_name, owner_domain))
                else:
                    cursor.execute(sql, (owner_name, owner_domain, survey_id))
                result = cursor.fetchall()
        finally:
            connection.close()

        answer = []

        state_service = StateService()
        for instance_tuple in result:
            if status is not None:
                answer.append(instance_tuple[0])
            else:
                instance = Instance.from_tuple(instance_tuple)
                state = state_service.get_next_state_in_instance(instance.instance_id, status)

                if state is not None:
                    answer.append(instance_tuple[0])


        return answer

    def get_survey_id(self, instance_id):
        instance = self.get_instance(instance_id)

        if instance is not None:
            return instance.survey_id

        return None

    def get_current_instance_ids(self):
        sql = "SELECT instance_id FROM instance"

        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
        finally:
            connection.close()

        answer = []

        for t in result:
            answer.append(t[0])

        return answer

    def start_instance(self, instance_id, state_service=None):
        print("Starting instance " + str(instance_id))

        if state_service is None:
            state_service = StateService()

        instance = self.get_instance(instance_id)
        survey = SurveyService().get_survey(instance.survey_id)
        first_question = ProtocolService().get_protocol(survey.protocol_id).first_question

        state_service.create_state(instance_id, first_question, Status.CREATED_START, 0)

        participant = ParticipantService().get_participant(survey.participant_id)
        PluginService().poke(participant.plugin_id, survey.survey_id)

    def run_loop(self):
        print("Starting instance service loop")
        while True:
            print("Running instance service loop")
            instance_ids = self.get_current_instance_ids()
            state_service = StateService()

            not_started = []
            in_progress = []
            finished = []

            for instance_id in instance_ids:
                latest = state_service.get_next_state_in_instance(instance_id)

                if latest is None:
                    not_started.append(instance_id)
                else:
                    in_progress.append(instance_id)

            for instance_id in in_progress:
                unfinished = state_service.get_unfinished_states(instance_id)

                if len(unfinished) is 0:
                    finished.append(instance_id)

            if len(finished) > 0:
                print("Instances that have finished: " + str(finished))

                self.delete_instances(finished)
                state_service.delete_states_for_instances(finished)

            if len(not_started) > 0:
                print ("Instances that have not started: " + str(not_started))

                for instance_id in not_started:
                    self.start_instance(instance_id, state_service)

            time.sleep(60)
