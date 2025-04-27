# db_connection.py

import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='banking_system'
        )
        if conn.is_connected():
            print("Connection successful!")
        return conn
    except Error as err:
        print(f"Error: {err}")
        return None
