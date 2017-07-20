import os
import time
import pymysql

from smsurvey.core.model.plugin.plugin import Plugin
from smsurvey.core.services.owner_service import OwnerService
from smsurvey.core.security import secure


class PluginService:

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD")):
        self.database_url = database_url
        self.database_username = database_username
        self.database_password = database_password
        self.database = "dbase"

    def get_plugin(self, plugin_id):
        sql = "SELECT * from plugin WHERE plugin_id = %s"
        connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                     host=self.database_url, database=self.database, charset="utf8")

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, plugin_id)
                result = cursor.fetchall()
        finally:
            connection.close()

        if len(result) > 0:
            plugin_sql = result[0]
            return Plugin.from_tuple(result)

        return None

    def validate_plugin(self, plugin_id, owner_name, owner_domain, token):
        plugin = self.get_plugin(plugin_id)

        if plugin is not None:
            if owner_name == plugin.owner_name and owner_domain == plugin.owner_domain:
                test = secure.encrypt_password(token, plugin.salt).decode()
                return test == plugin.token

        return False

    def is_plugin_registered(self, plugin_id):
        return self.get_plugin(plugin_id) is not None

    def register_plugin(self, owner_name, owner_domain, owner_password, plugin_id, permissions):
        if self.is_plugin_registered(plugin_id):
            raise secure.SecurityException("Plugin already registered")

        owner_service = OwnerService()

        if owner_service.does_owner_exist(owner_name, owner_domain):
            if owner_service.validate_password(owner_name, owner_domain, owner_password):
                salt = os.urandom(16)
                token = secure.encrypt_password(owner_domain + owner_name + str(time.time()), salt).decode()
                salt_for_token = os.urandom(16)
                salted_token = secure.encrypt_password(token, salt_for_token).decode()

                sql = "INSERT INTO plugin VALUES(%s, %s, %s, %s, %s, %s)"
                connection = pymysql.connect(user=self.database_username, password=self.database_password,
                                             host=self.database_url, database=self.database, charset="utf8")

                try:
                    with connection.cursor() as cursor:
                        cursor.execute(sql, (plugin_id, owner_name, owner_domain, salted_token, salt_for_token,
                                             permissions))
                        connection.commit()
                        cursor.fetchall()
                finally:
                    connection.close()

                return token
            else:
                raise secure.SecurityException("Unable to validate owner")
        else:
            raise secure.SecurityException("Owner does not exist")
