from smsurvey.core.model.query.dao import DAO


def selection(table_name, where_clause):
    sql = "SELECT FROM %s WHERE " + where_clause.build()
    connection = DAO.get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, table_name)
            result = cursor.fetchall()
    finally:
        connection.close()

    return result


def insert(table_name, columns, values):
    sql = "INSERT INTO %s %s VALUES %s"
    connection = DAO.get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (table_name, columns, values))
            connection.commit()
            cursor.fetchall()
    finally:
        connection.close()


def update(table_name):
    print("Noov")