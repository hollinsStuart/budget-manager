import sqlite3
from datetime import datetime, timedelta

rate_db_path = './data/exchange_rate.db'
transaction_db_path = './data/transactions.db'

def get_recent_transactions():
    """Fetch the 5 most recent transactions"""
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT date, merchant, amount, category FROM transactions ORDER BY id DESC LIMIT 3')
    transactions = cursor.fetchall()
    conn.close()
    return transactions


# Function to calculate the total expenses for the current month
def get_monthly_expenses():
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE date LIKE ?', (current_month + '%',))
    total_expense = cursor.fetchone()[0] or 0  # Return 0 if there are no expenses
    conn.close()
    return total_expense


def get_date_of_last_tenth():
    """Fetch the date of the last tenth of the month"""
    today = datetime.now()
    
    # If today is before the 10th, we need to go back to the previous month
    if today.day < 10:
        # Calculate the first day of the current month
        first_of_current_month = today.replace(day=1)
        # Go back one day to get the last day of the previous month
        last_day_of_previous_month = first_of_current_month - timedelta(days=1)
        # Return the 10th of the previous month
        return last_day_of_previous_month.replace(day=10).strftime('%Y-%m-%d')
    else:
        # If today is on or after the 10th, return the 10th of the current month
        return today.replace(day=10).strftime('%Y-%m-%d')


def get_expense_since_last_tenth():
    """Fetch the total expenses since the last tenth of the month"""
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    
    tenth_day_of_month = get_date_of_last_tenth()
    print(tenth_day_of_month)

    cursor.execute('SELECT SUM(amount) FROM transactions WHERE date >= ?', (tenth_day_of_month,))
    
    total_expense = cursor.fetchone()[0] or 0  # Return 0 if there are no expenses
    conn.close()
    
    return total_expense


def list_all_since_last_tenth():
    """Fetch and list all transactions since the last tenth of the current month"""
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    
    # Get the date for the last 10th of the current month
    current_month = datetime.now().strftime('%Y-%m')
    last_month = int(current_month.split('-')[1]) - 1
    current_day = datetime.now().strftime('%d')

    if int(current_day) < 10:
        tenth_day_of_month = current_month + '-10'
    else:
        tenth_day_of_month = current_month + '-10'
    
    # Query to get all transactions since the 10th of the current month
    cursor.execute('SELECT date, merchant, amount, category FROM transactions WHERE date >= ?', (tenth_day_of_month,))
    
    # Fetch all results
    transactions = cursor.fetchall()
    
    conn.close()
    
    return transactions

last_update_time = None

