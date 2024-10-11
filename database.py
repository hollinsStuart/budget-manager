import sqlite3
from datetime import datetime, timedelta

from utils import *

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


def get_expense_since_last_tenth():
    """Fetch the total expenses since the last tenth of the month"""
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    
    tenth_day_of_month = get_date_of_last_tenth()

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


def list_expenses_in_detail():
    transaction_db_path = './data/transactions.db'
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    # Get the current date and the date 30 days ago
    current_date = datetime.now()
    date_30_days_ago = current_date - timedelta(days=30)
    
    # Modify the SQL query to select transactions from the last 30 days and sort them by time
    cursor.execute('''
        SELECT DISTINCT LOWER(merchant) FROM transactions
        WHERE date >= ?
    ''', (date_30_days_ago,))
    
    transactions = cursor.fetchall()
    merchants = {transaction[0] for transaction in transactions}
    merchant_sums = []
    for merchant in merchants:
        cursor.execute('''
            SELECT SUM(amount), COUNT(*) FROM transactions
            WHERE LOWER(merchant) = ? AND date >= ?
        ''', (merchant, date_30_days_ago))
        result = cursor.fetchone()
        total_spent = result[0]
        transaction_count = result[1]
        merchant_sums.append((merchant, total_spent, transaction_count))

    # Sort merchants by total spent in descending order
    merchant_sums.sort(key=lambda x: x[1], reverse=True)
    conn.close()

last_update_time = None

