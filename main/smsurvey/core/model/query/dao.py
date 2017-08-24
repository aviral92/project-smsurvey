import os
import pymysql


class DAO:
    class __DAO:
        def __init__(self, database_url, database_username, database_password, test):
            self.database_url = database_url
            self.database_username = database_username
            self.database_password = database_password

            if test:
                self.database = 'test'
            else:
                self.database = 'dbase'

    instance = None

    def __init__(self, database_url=os.environ.get("RDS_URL"), database_username=os.environ.get("RDS_USERNAME"),
                 database_password=os.environ.get("RDS_PASSWORD"), test=False):
        if DAO.instance is None:
            DAO.instance = DAO.__DAO(database_url, database_username, database_password, test)

    @staticmethod
    def get_connection():
        if DAO.instance is not None:
            return pymysql.connect(user=DAO.instance.database_username, password=DAO.instance.database_password,
                                   host=DAO.instance.database_url, database=DAO.instance.database, charset="utf8")
        else:
            raise DAOError("DAO must be initialized before getting connection")


class DAOError(Exception):
    pass
