import bcrypt  # Used to hash passwords
import psycopg2
import os  # Used to load key from .env file
from dotenv import load_dotenv
from psycopg2 import sql, errors, DatabaseError
from psycopg2.extras import DictCursor
from PSQL_Bank_System import get_connection

# Load environment variables from .env file
load_dotenv()    

DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST')
}

# class DBContextManager:
#     """Context manager for PostgreSQL database connections."""
#     def __enter__(self):
#         self.conn = psycopg2.connect(**DATABASE_CONFIG)
#         self.cursor = self.conn.cursor(cursor_factory=DictCursor)  # Use DictCursor
#         return self.cursor

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.conn.commit()
#         self.cursor.close()
#         self.conn.close()

# def get_connection():
#     """Establishes a connection to the PostgreSQL database."""
#     try:
#         conn = psycopg2.connect(**DATABASE_CONFIG)
#         return conn
#     except Exception as e:
#         print(f"Error connecting to PostgreSQL Database: {e}")
#         return None



def test_connection(email):
    conn = None
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cur.fetchone()
        print(user_data[1],user_data[2],user_data[4])
    except Exception as e:
        print(f"Error connecting to the PostgreSQL database: {e}")
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    test_connection('cjj@gmail.com')




#  cursor.execute("SELECT id, name, email, user_type, password FROM users WHERE email = %s", (email,))
#                 user_data = cursor.fetchone()
#                 if user_data:
#                     stored_hashed_password = user_data[4]  # Assuming the password is the fifth column
#                     # Now, compare the provided password with the stored hashed password
#                     if bcrypt.checkpw(plaintext_password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
#                         # If the password matches, return the user object without the password
#                         return User(user_data[0], user_data[1], user_data[2], user_data[3])
               














# def hash_password(password):
#     """Hash a password for storing."""
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(password.encode('utf-8'), salt)

# def verify_password(stored_password, provided_password):
#     """Verify a stored password against one provided by user."""
#     return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
