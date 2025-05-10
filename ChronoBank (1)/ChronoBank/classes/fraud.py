# fraud.py (Inside ChronoBank/observer/)

class FraudDetector:
    def __init__(self):
        self.history = []

    def check_transaction(self, transaction):
        self.history.append(transaction)

        # Detect time laundering: unusually large deposits
        if transaction['type'] == 'Deposit' and transaction['amount'] > 100000:
            return "Possible time laundering detected."

        # Rapid transfers: multiple transactions in short span
        if len(self.history) >= 3:
            last_three = self.history[-3:]
            if all(t['type'] == 'Transfer' for t in last_three):
                return "Rapid transfers detected."

        return None
