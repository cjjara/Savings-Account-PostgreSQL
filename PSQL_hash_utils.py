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
    'user': 'Carlos',
    'password': 'H2WZV5rCYfwX',
    'host': 'ep-solitary-moon-a2axi3v2.eu-central-1.aws.neon.tech',
    'database': 'savings'
}

class DBContextManager:
    """Context manager for PostgreSQL database connections."""
    def __enter__(self):
        self.conn = psycopg2.connect(**DATABASE_CONFIG)
        self.cursor = self.conn.cursor(cursor_factory=DictCursor)  # Use DictCursor
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

def get_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print(f"Success connecting to PostgreSQL Database: {e}")    
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL Database: {e}")
        return None


def hash_and_update_password_for_specific_user(email):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Fetch the user with the specified email
            cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                user_id, plain_password = user
                # Hash the password
                hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
                # Update the user record with the hashed password
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password.decode('utf-8'), user_id))
                conn.commit()
                print("Successfully updated the password.")
            else:
                print("User not found.")

    except Exception as e:
        print(f"Error updating user passwords: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # hash_and_update_password_for_specific_user()
    hash_and_update_password_for_specific_user('cjj@gmail.com')






















# def hash_password(password):
#     """Hash a password for storing."""
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(password.encode('utf-8'), salt)

# def verify_password(stored_password, provided_password):
#     """Verify a stored password against one provided by user."""
#     return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
