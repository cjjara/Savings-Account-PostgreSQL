import mysql.connector
from mysql.connector import Error

# Update these with your actual MySQL database credentials
DATABASE_CONFIG = {
    'user': 'Carlos',
    'password': 'ExitoFtk#672',
    'host': 'localhost',
    'database': 'savings',
    'raise_on_warnings': True
}

def test_database_connection(config):
    """Attempts to connect to the MySQL database and prints the result."""
    conn = None  # Define conn variable outside the try block
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print("Successfully connected to the database.")
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION();")
            db_version = cursor.fetchone()
            print("MySQL database version:", db_version[0])
            cursor.close()
        else:
            print("Failed to connect to the database.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn and conn.is_connected():  # Check if conn is not None and is connected
            conn.close()
            print("MySQL connection is closed.")

# Run the test
test_database_connection(DATABASE_CONFIG)
