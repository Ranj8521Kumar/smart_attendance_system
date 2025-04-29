import mysql.connector
from mysql.connector import Error
from app.config import DB_CONFIG

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def close_connection(connection, cursor=None):
    """
    Close database connection and cursor
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
