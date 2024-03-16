import streamlit as st
import pandas as pd
from DB_banking_system import User, Account, Transaction, get_connection, authenticate_user
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
                st.experimental_rerun()  # Refresh state
            else:
                st.sidebar.error("Invalid login credentials.")
    else:
        logged_in_user = st.session_state['logged_in_user']
        st.sidebar.write(f"Welcome, {logged_in_user.name} ({logged_in_user.user_type})")
        if st.sidebar.button('Logout'):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

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
            user = User(name, email, user_type, password)
            user.save()
            st.success("User created successfully.")

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





#Working version using MySQL before changing the program flow

# def main():
#     st.title("Banking System")

#     # Main Menu
#     choice = st.sidebar.selectbox("Menu", ["Create User", "Login", "Manage Account"])

#     if choice == "Create User":
#         create_user_form()

#     elif choice == "Manage Account":
#         user_id = select_user()
#         if user_id:
#             manage_account(user_id)

# def create_user_form():
#     with st.form("Create User"):
#         name = st.text_input("Name")
#         email = st.text_input("Email")
#         #User type only used to create admin user
#         # user_type = st.selectbox("User Type", ["Customer", "Admin"])
#         password = st.text_input("Password", type="password")  # Hash this in production
#         submitted = st.form_submit_button("Create User")
#         if submitted:
#             new_user = User(name, email, user_type, password)
#             new_user.save()
#             st.success(f"User '{name}' created successfully!")

# def select_user():
#     users = load_users()
#     user_id = st.selectbox("Select User", list(users.keys()), format_func=lambda x: users[x])
#     return user_id

# def manage_account(user_id):
#     account_action = st.radio("Action", ["Create Account", "Deposit", "Withdraw", "View Transactions"])
#     if account_action == "Create Account":
#         create_account(user_id)
#     else:
#         account_id = select_account(user_id)
#         if account_id:
#             if account_action == "Deposit":
#                 deposit_to_account(account_id)
#             elif account_action == "Withdraw":
#                 withdraw_from_account(account_id)
#             elif account_action == "View Transactions":
#                 view_transactions(account_id)

# def create_account(user_id):
#     with st.form("Account Details"):
#         acc_type = st.text_input("Account Type")
#         balance = st.number_input("Initial Balance", min_value=0.0, value=0.0, step=0.01)
#         interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=0.0, step=0.01)
#         submitted = st.form_submit_button("Create Account")
#         if submitted:
#             account = Account(acc_type, balance, interest_rate, user_id)
#             account.save()
#             st.success(f"Account created successfully for user ID {user_id}.")

# def deposit_to_account(account_id):
#     amount = st.number_input("Deposit Amount", min_value=0.01, value=0.0, step=0.01)
#     description = "Deposit"
#     if st.button("Deposit"):
#         account = Account.load(account_id)
#         account.deposit(amount, description)
#         st.success(f"Deposited ${amount:.2f} to account {account_id}.")

# def withdraw_from_account(account_id):
#     amount = st.number_input("Withdrawal Amount", min_value=0.01, value=0.0, step=0.01)
#     description = "Withdrawal"
#     if st.button("Withdraw"):
#         account = Account.load(account_id)
#         account.withdraw(amount, description)
#         st.success(f"Withdrew ${amount:.2f} from account {account_id}.")

# def view_transactions(account_id):
#     transactions = Transaction.get_transaction_history(account_id)
#     if transactions:
#         for t in transactions:
#             st.write(f"{t.timestamp} - {t.type}: ${t.amount:.2f}, {t.description}")
#     else:
#         st.write("No transactions found.")

# def load_users():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT id, name FROM users')
#     users = {user_id: name for user_id, name in cursor.fetchall()}
#     cursor.close()
#     conn.close()
#     return users

# def select_account(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT id, acc_type FROM accounts WHERE owner_id = %s', (user_id,))
#     accounts = {acc_id: acc_type for acc_id, acc_type in cursor.fetchall()}
#     cursor.close()
#     conn.close()
#     account_id = st.selectbox("Select Account", list(accounts.keys()), format_func=lambda x: accounts[x])
#     return account_id

# if __name__ == "__main__":
#     main()












#old version using sqlite - use this to figure out formating using pandas and columns

# def main():
#     st.title("Jara Bank")

#     # Main Menu
#     choice = st.sidebar.selectbox("Menu", ["Create Account", "Manage Account"])

#     if choice == "Create Account":
#         with st.form("Create Account"):
#             name = st.text_input("Account Name")
#             initial_balance = st.number_input("Initial Balance", min_value=0.0, format="%.2f")
#             interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, format="%.2f")
#             submitted = st.form_submit_button("Create Account")
#             if submitted:
#                 if Account.load(name) is None:
#                     Account(name, initial_balance, interest_rate).save()
#                     st.success(f"Account '{name}' created successfully!")
#                 else:
#                     st.error("Account already exists.")

#     elif choice == "Manage Account":
#         account_names = Account.get_all_account_names()
#         account_name = st.sidebar.selectbox("Select an Account", account_names)
#         if account_name:
#             account = Account.load(account_name)
#             col1, col2, col3 = st.columns(3)
#             if account:
#                 st.session_state["account"] = account  # Save the loaded account to session state
#                 # st.write(f"Current Balance: ${account.get_balance():.2f}")
#                 col1.metric(label="Owner", value=account_name)
#                 col2.metric(label="Current Balance: $", value="{:,.2f}".format(account.get_balance()))
#                 col3.metric(label="Current Interest: %", value="{:,.2f}".format(account.get_intrate()))

#                 activity = st.sidebar.selectbox("Select Activity", ["Deposit", "Withdraw", "Set Interest Rate", "View Transactions"])
#                 handle_activity(account, activity)
#             else:
#                 st.error("Account not found. Please select a valid account.")

# def handle_activity(account, activity):
#     if activity == "Deposit":
#         deposit_amount = st.number_input("Amount to deposit", min_value=0.01, format="%.2f")
#         deposit_description = st.text_input("Description")
#         if st.button("Deposit"):
#             account.deposit(deposit_amount, deposit_description)
#             st.success(f"Deposited ${deposit_amount:.2f} to {account.name}")
#             st.write(f"Updated Balance: ${account.get_balance():.2f}")
#             st.balloons

#     elif activity == "Withdraw":
#         withdraw_amount = st.number_input("Amount to withdraw", min_value=0.01, format="%.2f")
#         withdraw_description = st.text_input("Description")
#         if st.button("Withdraw"):
#             try:
#                 account.withdraw(withdraw_amount, withdraw_description)
#                 st.success(f"Withdrew ${withdraw_amount:.2f} from {account.name}")
#                 st.write(f"Updated Balance: ${account.get_balance():.2f}")
#             except ValueError as e:
#                 st.error(e)

#     elif activity == "Set Interest Rate":
#         new_rate = st.number_input("New Interest Rate (%)", min_value=0.0, format="%.2f")
#         if st.button("Set Rate"):
#             account.set_interest_rate(new_rate)
#             st.success(f"Interest rate updated to {new_rate}% for {account.name}")

#     elif activity == "View Transactions":
#         transactions = account.get_transaction_history(account.name)
#         # for t in transactions:
#         #     st.write(f"{t[0]} - {t[1]}: ${t[2]:.2f}, Description: {t[3]}")
#         if transactions:
#             # Convert transactions list to a DataFrame for better display
#             # import pandas as pd

#             # Assuming transaction structure: [timestamp, type, amount, description]
#             df = pd.DataFrame(transactions, columns=['Timestamp', 'Type', 'Amount', 'Description'])
            
#             # Optionally, you can format the 'Amount' column to display as currency
#             df['Amount'] = df['Amount'].apply(lambda x: f"${x:.2f}")
            
#             st.dataframe(df)
#         else:
#             st.write("No transactions found for this account.")


# if __name__ == "__main__":
#     main()
