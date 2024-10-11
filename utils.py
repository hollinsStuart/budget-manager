from datetime import datetime
import re


def parse_transaction(text):
    """
    Parse transactions from text.

    Returns a list of dictionaries containing transaction data.
    """
    pattern = r'(\d{4}年\d{2}月\d{2}日).+?在(.+?)(消费|预授权)USD([0-9.]+)元'
    matches = re.findall(pattern, text)

    transactions = []
    for match in matches:
        date = match[0].replace('年', '-').replace('月', '-').replace('日', '')
        merchant = match[1].strip()
        verb = match[2].strip()
        amount = float(match[3])

        if verb not in ['消费', '预授权']:
            raise ValueError(f"Unrecognized verb: {verb} in transaction text.")

        transactions.append({
            'date': date,
            'merchant': merchant,
            'amount': amount,
            'type': 'pre-authorization' if verb == '预授权' else 'consumption',
            'category': ''
        })

    return transactions


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
