import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Update these with your actual MySQL database credentials
DATABASE_CONFIG = {
    'user': 'Carlos',
    'password': 'ExitoFtk#672',
    'host': 'localhost',
    'database': 'savings',
    'raise_on_warnings': True
}

class DBContextManager:
    """Context manager for MySQL database connections."""
    def __enter__(self):
        self.conn = mysql.connector.connect(**DATABASE_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

def get_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

class User:
    """Represents a user in the banking application."""
    def __init__(self, name, email, user_type, password, user_id=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.user_type = user_type
        self.password = password  # Hash passwords in production

    def save(self):
        """Saves the user to the database."""
        with DBContextManager() as cursor:
            cursor.execute('''
                INSERT INTO users (name, email, user_type, password)
                VALUES (%s, %s, %s, %s)
            ''', (self.name, self.email, self.user_type, self.password))
            self.user_id = cursor.lastrowid


class Account:
    def __init__(self, acc_type, balance, interest_rate, owner_id, last_transaction_time=None, acc_id=None):
        self.acc_id = acc_id
        self.acc_type = acc_type
        self.balance = balance
        self.interest_rate = interest_rate
        self.owner_id = owner_id
        self.last_transaction_time = last_transaction_time if last_transaction_time else datetime.now()

    @staticmethod
    def load(acc_id):
        """Load an account from the database by its account ID, with error handling."""
        try:
            with DBContextManager() as cursor:
                cursor.execute('SELECT acc_type, balance, interest_rate, owner_id, last_transaction_time, id FROM accounts WHERE id = %s', (acc_id,))
                account_data = cursor.fetchone()
                if account_data:
                    return Account(
                        acc_type=account_data['acc_type'],
                        balance=account_data['balance'],
                        interest_rate=account_data['interest_rate'],
                        owner_id=account_data['owner_id'],
                        last_transaction_time=account_data['last_transaction_time'],
                        acc_id=account_data['id']
                    )
                else:
                    return None
        except Error as e:
            print(f"Database error during account load: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during account load: {e}")
            return None


    def calc_interest(self):
        """Calculate and apply interest based on the time since the last transaction or interest rate change."""
        current_time = datetime.now()
        elapsed_time_in_days = (current_time - self.last_transaction_time).total_seconds() / (24 * 3600)
        daily_interest_rate = self.interest_rate / 100 / 365
        interest = self.balance * (1 + daily_interest_rate) ** elapsed_time_in_days - self.balance
        self.balance += interest
        return interest

    def apply_interest(self):
        """Apply interest before any balance change."""
        interest = self.calc_interest()
        if interest > 0:
            self.record_transaction("Interest", interest, "Interest applied")

    def deposit(self, amount, description="Deposit"):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.apply_interest()
        self.balance += amount
        self.record_transaction("Deposit", amount, description)
        self.last_transaction_time = datetime.now()
        self.save()

    def withdraw(self, amount, description="Withdrawal"):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.apply_interest()
        self.balance -= amount
        self.record_transaction("Withdrawal", amount, description)
        self.last_transaction_time = datetime.now()
        self.save()

    def set_interest_rate(self, new_rate, description="Interest Rate Change"):
        if new_rate < 0:
            raise ValueError("Interest rate cannot be negative.")
        self.apply_interest()  # Apply any accrued interest at the old rate before changing it
        self.interest_rate = new_rate
        self.record_transaction("Interest Rate Change", 0, description)
        self.last_transaction_time = datetime.now()
        self.save()

    def record_transaction(self, transaction_type, amount, description):
        """Records a new transaction in the database."""
        with DBContextManager() as cursor:
            cursor.execute('''
                INSERT INTO transactions (acct_id, amount, type, description, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            ''', (self.acc_id, amount, transaction_type, description, datetime.now()))

    def save(self):
        """Saves or updates the account in the database."""
        with DBContextManager() as cursor:
            if self.acc_id is None:
                cursor.execute('''
                    INSERT INTO accounts (acc_type, balance, interest_rate, last_transaction_time, owner_id)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (self.acc_type, self.balance, self.interest_rate, self.last_transaction_time, self.owner_id))
                self.acc_id = cursor.lastrowid
            else:
                cursor.execute('''
                    UPDATE accounts SET balance = %s, interest_rate = %s, last_transaction_time = %s, owner_id = %s
                    WHERE id = %s
                ''', (self.balance, self.interest_rate, self.last_transaction_time, self.owner_id, self.acc_id))


class Transaction:
    """Represents a transaction made against a bank account."""
    def __init__(self, acct_id, amount, transaction_type, description, timestamp=None, transaction_id=None):
        self.transaction_id = transaction_id
        self.acct_id = acct_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.timestamp = timestamp if timestamp else datetime.now()

    def save(self):
        """Records the transaction in the database."""
        with DBContextManager() as cursor:
            cursor.execute('''
                INSERT INTO transactions (acct_id, amount, type, timestamp, description)
                VALUES (%s, %s, %s, %s, %s)
            ''', (self.acct_id, self.amount, self.transaction_type, self.timestamp, self.description))
            self.transaction_id = cursor.lastrowid

# Example usage
if __name__ == '__main__':
    print("This script is intended to be imported as a module, not run directly.")