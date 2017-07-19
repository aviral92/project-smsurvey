import pymysql
import os

database_url = os.environ.get("RDS_URL")
database_username = os.environ.get("RDS_USERNAME")
database_password = os.environ.get("RDS_PASSWORD")


def clear(table_name):
    sql = 'DELETE FROM %s'
    connection = pymysql.connect(user=database_username, password=database_password, host=database_url,
                                 database='dbase')

    print("Clearing out " + table_name + " table")

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (table_name))
            cursor.fetchall()
    finally:
        connection.close()