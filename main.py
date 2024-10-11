import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime

import rate

from database import get_recent_transactions, get_monthly_expenses, get_expense_since_last_tenth
from utils import *

# Ensure /data folder exists
if not os.path.exists('./data'):
    os.makedirs('./data')

# SQLite database path
transaction_db_path = './data/transactions.db'
budget = 3000

# Function to create the table if it doesn't exist
def create_transaction_db():
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            merchant TEXT,
            amount REAL,
            category TEXT DEFAULT 'None'
        )
    ''')
    conn.commit()
    conn.close()


def insert_transactions(transactions):
    """Insert transactions into the database"""
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    
    # Insert transaction data, ignoring duplicates (based on date, merchant, and amount)
    for txn in transactions:
        cursor.execute('''
            INSERT INTO transactions (date, merchant, amount, category)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS(
                SELECT 1 FROM transactions WHERE date=? AND merchant=? AND amount=?
            )
        ''', (txn['date'], txn['merchant'], txn['amount'], txn['category'], txn['date'], txn['merchant'], txn['amount']))
    
    conn.commit()
    conn.close()


def process_input(text):
    transactions = parse_transaction(text)
    insert_transactions(transactions)


def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_data = file.read()
        process_input(text_data)
        messagebox.showinfo("Success", "Transactions loaded and stored in the database!")


def manual_input():
    text_data = simpledialog.askstring("Input", "Please input your bank transaction texts (in one line):")
    if text_data:
        process_input(text_data)
        messagebox.showinfo("Success", "Transactions inputted and stored in the database!")
        update_display()


def categorize_transactions():
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT merchant FROM transactions WHERE category = ""')
    merchants = cursor.fetchall()
    
    for merchant in merchants:
        merchant_name = merchant[0]
        category = simpledialog.askstring("Category", f"Enter category for {merchant_name}:")
        if category:
            cursor.execute('UPDATE transactions SET category = ? WHERE merchant = ?', (category, merchant_name))
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Categories updated!")


# Function to toggle between CNY and USD
def toggle_currency():
    global show_in_usd
    show_in_usd = not show_in_usd
    update_display()


# Function to update the display based on the selected currency
def update_display():
    recent_transactions = get_recent_transactions()
    monthly_expenses = get_expense_since_last_tenth()

    # Get the latest exchange rate
    exchange_rate = rate.get_last_exchange_rate()['rate']

    # Clear the current content of the display
    for widget in frame.winfo_children():
        widget.destroy()

    # Display 5 most recent transactions
    tk.Label(frame, text="Recent Transactions:", font=("Helvetica", 16), anchor="w", justify="left").pack(fill="x", pady=5)
    for txn in recent_transactions:
        date, merchant, amount, category = txn
        if show_in_usd:
            label_text = f"{date:<15} {merchant:<20} USD {amount:>8}"
        else:
            amount_in_cnyusd = round(amount * exchange_rate, 2)
            label_text = f"{date:<15} {merchant:<20} CNY {amount_in_cnyusd:>8}"
        tk.Label(frame, text=label_text).pack()

    # Display monthly budget and expenses
    tk.Label(frame, text="").pack()  # Empty line for spacing
    total_remaining = budget - monthly_expenses
    if show_in_usd:
        tk.Label(frame, text=f"Monthly Budget: USD {budget}", font=("Helvetica", 12)).pack()
        tk.Label(frame, text=f"Expenses This Month: USD {monthly_expenses:.2f}", font=("Helvetica", 12)).pack()
        tk.Label(frame, text=f"Remaining Budget: USD {total_remaining:.2f}", font=("Helvetica", 12)).pack()
    else:
        total_remaining_cny = round(total_remaining * exchange_rate, 2)
        monthly_expenses_cny = round(monthly_expenses * exchange_rate, 2)
        tk.Label(frame, text=f"Monthly Budget: CNY {budget * exchange_rate}", font=("Helvetica", 12)).pack()
        tk.Label(frame, text=f"Expenses This Month: CNY {monthly_expenses_cny:.2f}", font=("Helvetica", 12)).pack()
        tk.Label(frame, text=f"Remaining Budget: CNY {total_remaining_cny:.2f}", font=("Helvetica", 12)).pack()
    # Add a label for the budget usage
    spent_label = tk.Label(frame, text="", font=("Helvetica", 12))
    spent_label.pack(pady=5)

    # Add a progress bar to indicate budget usage
    progress_bar = ttk.Progressbar(frame, orient='horizontal', length=300, mode='determinate')
    progress_bar.pack(pady=10)
    update_budget_bar(progress_bar, spent_label)
    
    # Load file button
    load_button = tk.Button(frame, text="Load Transactions from File", command=load_file)
    load_button.pack(pady=10)

    # Manual input button
    input_button = tk.Button(frame, text="Manually Input Transactions", command=manual_input)
    input_button.pack(pady=10)

    # Categorize button
    category_button = tk.Button(frame, text="Categorize Transactions", command=categorize_transactions)
    category_button.pack(pady=10)


def refresh_window():
    """Refresh the displayed transactions and other data in the window"""
    # Clear the current frame (e.g., remove existing widgets)
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Fetch and display the updated data from the database
    update_display()


def check_for_db_changes():
    global last_update_time
    
    # Query the last updated time from the database (e.g., a timestamp of the last transaction)
    conn = sqlite3.connect(transaction_db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT MAX(last_updated) FROM transactions')  # Example query
    latest_update = cursor.fetchone()[0]
    conn.close()

    # If the database has been updated, refresh the window
    if latest_update != last_update_time:
        last_update_time = latest_update
        refresh_window()
    
    # Check again after 5000 milliseconds (5 seconds)
    root.after(5000, check_for_db_changes)


def update_budget_bar(progress_bar, spent_label):
    total_spent = get_expense_since_last_tenth()

    # Calculate the percentage of the budget used
    budget_used_percentage = (total_spent / budget) * 100
    budget_used_percentage = min(budget_used_percentage, 100)  # Cap it at 100%

    # Update the progress bar value
    progress_bar['value'] = budget_used_percentage
    spent_label['text'] = f"Spent {budget_used_percentage:.2f} % of the budgets."
    # Update the label showing the spent amount and the budget


if __name__ == '__main__':
    # Initialize the database
    rate.create_exchange_rate_db()
    create_transaction_db()

    # Initialize the GUI
    root = tk.Tk()
    root.title("Bank Transaction Processor")

    frame = tk.Frame(root)
    frame.pack(pady=20, padx=20)

    # Add a button to toggle between CNY and USD
    show_in_usd = True
    toggle_button = tk.Button(root, text="CNY/USD", command=toggle_currency)
    toggle_button.pack(pady=10)

    # Call the update display function initially to show data
    update_display()
    # root.after(500, check_for_db_changes)  # Start polling after 5 seconds

    root.mainloop()
