import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables from .env file
load_dotenv()

def test_database_connection():
    """Tests the database connection using credentials from the .env file."""
    try:
        # Establish a database connection
        conn = mysql.connector.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME')
        )

        # Check if the connection was successful
        if conn.is_connected():
            print("Successfully connected to the database.")
        else:
            print("Failed to connect to the database.")
    except Error as e:
        # Print any error that occurs during the connection attempt
        print(f"Error connecting to the database: {e}")
    finally:
        # Ensure that the connection is closed after the check
        if conn.is_connected():
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    test_database_connection()
