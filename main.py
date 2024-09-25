import re
import pandas as pd

def parse_transaction(text):
    # Regex to capture date, merchant, and amount from the text
    pattern = r'(\d{4}年\d{2}月\d{2}日).+?在(.+?)消费USD([0-9.]+)元'
    matches = re.findall(pattern, text)
    
    # Convert date format and clean data
    transactions = []
    for match in matches:
        date = match[0].replace('年', '-').replace('月', '-').replace('日', '')
        merchant = match[1].strip()
        amount = float(match[2])
        transactions.append({'date': date, 'merchant': merchant, 'amount': amount})
    
    return transactions

def process_input(text):
    # Parse transactions
    transactions = parse_transaction(text)
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Remove duplicates based on date, merchant, and amount
    df.drop_duplicates(subset=['date', 'merchant', 'amount'], inplace=True)
    
    return df

if __name__ == "__main__":
    input_type = input("Enter 'file' to read from .txt or 'input' for system input: ").strip().lower()

    if input_type == 'file':
        file_path = input("Enter the path of the .txt file: ").strip()
        with open(file_path, 'r', encoding='utf-8') as file:
            text_data = file.read()
    elif input_type == 'input':
        print("Please input your bank transaction texts, end input with an empty line:")
        text_data = ""
        while True:
            line = input()
            if not line:
                break
            text_data += line + "\n"

    # Process the text
    df = process_input(text_data)
    
    # Output the result
    print(df)
