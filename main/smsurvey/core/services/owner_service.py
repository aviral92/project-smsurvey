import os
import pymysql

from smsurvey.core.security import secure
from smsurvey.core.model.survey.owner import Owner

class OwnerService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD")):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password
        self.database = 'dbase'

    def get(self, name, domain):
        sql = "SELECT * FROM owner WHERE name=%s AND domain=%s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (name, domain))
                result = cursor.fetchall()
        finally:
            connection.close()

        owner_sql = result[0]
        return Owner.from_tuple(owner_sql)

    def create_owner(self, name, domain, unsafe_password):
        sql = "INSERT INTO owner VALUES(%s, %s, %s, %s, %s)"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database)

        salt = os.urandom(16)
        password = secure.encrypt_password(unsafe_password, salt)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, (name, domain, password, salt))
                connection.commit()
                cursor.fetchall()
        finally:
            connection.close()

    def does_owner_exist(self, name, domain):
        return self.get(name, domain) is not None

    def validate_password(self, name, domain, password):
        owner = self.get(name, domain)

        if owner is not None:
            test = secure.encrypt_password(password, owner.salt).decode()
            return test == owner.password
