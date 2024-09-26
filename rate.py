import requests
import sqlite3
from datetime import datetime

# SQLite database path
db_path = './data/exchange_rate.db'


def create_exchange_rate_db():
    """Create the exchange rate table if it doesn't exist"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exchange_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rate REAL,
            last_updated TEXT
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM exchange_rate')
    if cursor.fetchone()[0] == 0:
        # Insert fake initial exchange rate data if the table is empty
        fake_rate = 7
        last_updated = "2002-09-12 15:30:54"
        cursor.execute('''
            INSERT INTO exchange_rate (rate, last_updated)
            VALUES (?, ?)
        ''', (fake_rate, last_updated))
    conn.commit()
    conn.close()


def get_current_exchange_rate():
    url = 'https://open.er-api.com/v6/latest/USD'  # Example API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        cny_rate = data['rates']['CNY']

        # Store the fetched exchange rate in the database
        store_exchange_rate(cny_rate)

        return cny_rate
    else:
        raise Exception("Failed to fetch exchange rate")


# Function to store the exchange rate and last updated time in the database
def store_exchange_rate(rate):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current time
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert the exchange rate and timestamp into the database
    cursor.execute('''
        INSERT INTO exchange_rate (rate, last_updated)
        VALUES (?, ?)
    ''', (rate, last_updated))
    
    conn.commit()
    conn.close()

# Function to get the latest stored exchange rate and last updated time
def get_last_exchange_rate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT rate, last_updated FROM exchange_rate ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return {'rate': result[0], 'last_updated': result[1]}
    else:
        return None
