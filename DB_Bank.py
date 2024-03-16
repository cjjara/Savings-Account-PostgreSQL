import streamlit as st
import pandas as pd
from DB_banking_system import User, Account, Transaction, get_connection, authenticate_user, create_user_flow
from datetime import datetime


def main():
    st.sidebar.image('gem.svg', width=50)   
    st.sidebar.title("JADE Bank")

    # Login Section
    if 'logged_in_user' not in st.session_state:
        user_email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = authenticate_user(user_email, password)
            if user:
                st.session_state['logged_in_user'] = user
                st.rerun()  # Refresh state
            else:
                st.sidebar.error("Invalid login credentials.")
    else:
        logged_in_user = st.session_state['logged_in_user']
        st.sidebar.write(f"Welcome, {logged_in_user.name} ({logged_in_user.user_type})")
        if st.sidebar.button('Logout'):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if 'logged_in_user' in st.session_state:
        user = st.session_state['logged_in_user']
        if user.user_type == "customer":
            customer_flow(user)
        elif user.user_type == "admin":
            admin_flow()

def admin_flow():
    st.sidebar.subheader("Admin Panel")
    admin_action = st.sidebar.radio("Admin Actions", ["Manage Existing User", "Create New User"])

    if admin_action == "Manage Existing User":
        manage_existing_user()
    elif admin_action == "Create New User":
        create_new_user()


def customer_flow(user):
    # st.write(f"Welcome, {user.name} !")
    st.divider()
    account_id = select_account(user.user_id)
    if account_id:
        display_account_details(account_id)
        if st.button("View Transactions"):
            display_transactions(account_id)

def create_new_user():
    with st.form("Create New User"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        user_type = st.selectbox("User Type", ["user", "admin"])
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Create User")

        if submit_button:
            try:
                create_user_flow(name, email, user_type, password)
                st.success("User created successfully.")
            except Exception as e:
                st.error(str(e))  # Display the error message provided by the exception


def manage_existing_user():
    user_id = select_user()
    if user_id:
        user_action = st.radio("Actions for Selected User", ["Select Account","Create New Account"])
        if user_action == "Create New Account":
            create_account(user_id)
        elif user_action == "Select Account":
            account_id = select_account(user_id)
            if account_id:
                display_account_details(account_id)
                admin_account_actions(account_id)


def create_account(user_id):
    with st.form("Account Details"):
        acc_type = st.text_input("Account Type")
        balance = st.number_input("Initial Balance", min_value=0.0, value=0.0, step=0.01)
        interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=0.0, step=0.01)
        submitted = st.form_submit_button("Create Account")
        if submitted:
            # Assuming Account class has a constructor that matches these parameters
            account = Account(acc_type=acc_type, balance=balance, interest_rate=interest_rate, owner_id=user_id)
            account.save()
            st.success(f"Account created successfully for user ID {user_id}.")

def select_user():
    conn = get_connection()
    cursor = conn.cursor()
    # cursor.execute("SELECT id, name FROM users WHERE user_type = 'customer'")
    cursor.execute("SELECT id, name FROM users")
    users = {user_id: name for user_id, name in cursor.fetchall()}
    cursor.close()
    conn.close()
    
    user_ids = list(users.keys())
    user_names = [users[uid] for uid in user_ids]
    
    # Use index position for value and a callback to update session state on selection
    selected_index = st.sidebar.selectbox("Select User", range(len(user_ids)), format_func=lambda x: user_names[x])
    selected_user_id = user_ids[selected_index]
    
    # Update session state when a new user is selected
    if 'selected_user_id' not in st.session_state or st.session_state.selected_user_id != selected_user_id:
        st.session_state.selected_user_id = selected_user_id
        st.session_state.selected_account_id = None  # Reset selected account ID if user changes
    
    return selected_user_id

def select_account(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, acc_type FROM accounts WHERE owner_id = %s", (user_id,))
    accounts = {acc_id: acc_type for acc_id, acc_type in cursor.fetchall()}
    cursor.close()
    conn.close()
    
    if accounts:
        account_ids = list(accounts.keys())
        account_types = [accounts[aid] for aid in account_ids]
        
        selected_index = st.sidebar.selectbox("Select Account", range(len(account_ids)), format_func=lambda x: account_types[x], key="account_select")
        selected_account_id = account_ids[selected_index]
        
        # Update session state for the selected account
        if 'selected_account_id' not in st.session_state or st.session_state.selected_account_id != selected_account_id:
            st.session_state.selected_account_id = selected_account_id
            
        return selected_account_id
    else:
        # Reset or clear the account selection in session state if no accounts are found
        st.session_state.selected_account_id = None
        return None

def display_account_details(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT acc_type, balance, interest_rate FROM accounts WHERE id = %s", (account_id,))
    acc_details = cursor.fetchone()
    cursor.close()
    conn.close()
    if acc_details:
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Account", value=acc_details[0])
        col2.metric(label="Current Balance: $", value="{:,.2f}".format(acc_details[1]))
        col3.metric(label="Current Interest: %", value="{:,.1f}".format(acc_details[2]))
        st.divider()

def display_transactions(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, type, amount, description FROM transactions WHERE acct_id = %s", (account_id,))
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    if transactions:
        df = pd.DataFrame(transactions, columns=['Timestamp', 'Type', 'Amount', 'Description'])
        st.table(df)
    else:
        st.write("No transactions found.")

def admin_account_actions(account_id):
    st.subheader("Account Actions")
    action = st.selectbox("Choose Action", ["Deposit", "Withdraw", "Change Interest Rate", "View Transactions", "Light On"])

    if action == "Deposit":
        # Adjust the default value to match or exceed min_value
        deposit_amount = st.number_input("Amount to Deposit", min_value=1.00, value=1.00, step=1.00)
        deposit_description = st.text_input("Description for Deposit", value="Admin deposit")
        if st.button("Confirm Deposit"):
            make_deposit(account_id, deposit_amount, deposit_description)

    elif action == "Withdraw":
        # Adjust the default value to match or exceed min_value
        withdraw_amount = st.number_input("Amount to Withdraw", min_value=1.00, value=1.00, step=1.00)
        withdraw_description = st.text_input("Description for Withdrawal", value="Admin withdrawal")
        if st.button("Confirm Withdrawal"):
            make_withdrawal(account_id, withdraw_amount, withdraw_description)

    elif action == "Change Interest Rate":
        # Here, if your interest rate can be 0%, adjust accordingly
        new_interest_rate = st.number_input("New Interest Rate (%)", min_value=0.0, value=0.0, step=0.01)
        if st.button("Update Interest Rate"):
            update_interest_rate(account_id, new_interest_rate)

    elif action == "View Transactions":
        # To view a list of transactions
        display_transactions(account_id)
    
    elif action == "Light On":
        if st.button("Confirm $1 Light Penalty"):
            make_withdrawal(account_id, 1.00, "Light left on")

def make_deposit(account_id, amount, description):
    try:
        account = Account.load(account_id)
        account.deposit(amount, description)
        st.success(f"Deposited ${amount:.2f} to account ID {account_id}.")
    except Exception as e:
        st.error(f"Error during deposit: {e}")

def make_withdrawal(account_id, amount, description):
    try:
        account = Account.load(account_id)
        account.withdraw(amount, description)
        st.success(f"Withdrew ${amount:.2f} from account ID {account_id}.")
    except Exception as e:
        st.error(f"Error during withdrawal: {e}")

def update_interest_rate(account_id, new_rate):
    try:
        account = Account.load(account_id)
        account.interest_rate = new_rate  # Assuming Account class has a method to update interest rate or you directly set it here
        account.save()  # Make sure to save the updated account details
        st.success(f"Interest rate updated to {new_rate}% for account ID {account_id}.")
    except Exception as e:
        st.error(f"Error updating interest rate: {e}")

if __name__ == "__main__":
    main()





