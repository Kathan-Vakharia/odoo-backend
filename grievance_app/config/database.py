import mysql.connector
import os
from mysql.connector import Error


db_host = os.getenv('DB_HOST')
db_database = os.getenv('DB_DATABASE')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

print(db_host, db_database, db_user, db_password)


def create_db_conn():
    try:
        connection = mysql.connector.connect(
            host=db_host,
            database=db_database,
            user=db_user,
            password=db_password
        )
        if connection.is_connected():
            print("Successfully connected to the database")

    except Error as e:
        print(f"Error: {e}")
        os._exit(0)

    return connection


def close_conn(conn):

    if conn.is_connected():
        conn.close()
        print("MySQL connection is closed")
