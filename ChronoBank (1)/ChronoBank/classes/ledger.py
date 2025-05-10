# ledger.py (Inside `ChronoBank/classes`)
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'db.json')

class Ledger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.transactions = []
            cls._instance.user_id = None
        return cls._instance

    def load_user_transactions(self, user_id):
        self.user_id = user_id
        try:
            with open(DB_PATH, 'r') as f:
                data = json.load(f)
                for user in data["users"]:
                    if user["user_id"] == user_id:
                        self.transactions = user.get("transactions", [])
                        break
        except Exception as e:
            print("Error loading transactions:", e)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.save_transactions_to_db()

    def get_transactions(self):
        return self.transactions[-10:]
    
    def save_transactions_to_db(self):
        try:
            with open(DB_PATH, 'r') as f:
                data = json.load(f)
            for user in data["users"]:
                if user["user_id"] == self.user_id:
                    user["transactions"] = self.transactions
                    break
            with open(DB_PATH, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Error saving transactions:", e)
