import json

def save_transactions(transactions, filename="data/transactions.json"):
    with open(filename, "w") as f:
        json.dump(transactions, f)

def load_transactions(filename="data/transactions.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
 
