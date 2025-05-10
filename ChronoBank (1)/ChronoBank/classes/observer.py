# observer.py (Inside `ChronoBank/observer`)
import tkinter as tk
from tkinter import messagebox
#from ChronoBank.classes.ledger import Ledger
#from ChronoBank.classes.adapter import LegacyBankSystem, TimeAccountAdapter
#from ChronoBank.patterns.decorator import BasicTransaction, TimeTaxDecorator, BonusTimeDecorator

import datetime

class Observer:
    def update(self, message):
        pass

class UserNotification(Observer):
    def __init__(self, user):
        self.user = user

    def update(self, message):
        print(f"Notification for {self.user['name']}: {message}")

class Account:
    def __init__(self, account_id, balance=0, user=None):
        self.account_id = account_id
        self.balance = balance
        self.observers = []
        self.user = user
        self.transaction_history = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify(self, message):
        for observer in self.observers:
            observer.update(message)

    def deposit(self, amount):
        self.balance += amount
        self.record_transaction('Deposit', amount)
        self.check_balance()
        self.notify(f"Deposited {amount} time units. New balance: {round(self.balance, 2)}")

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.record_transaction('Withdraw', amount)
            self.check_balance()
            self.notify(f"Withdrew {amount} time units. New balance: {round(self.balance, 2)}")
        else:
            self.notify("Attempted withdrawal failed due to insufficient balance.")
            raise ValueError("Insufficient funds")

    def check_balance(self):
        if self.balance < 1000:  # You can set this threshold as needed
            self.notify("⚠️ Low balance warning! Consider depositing more time units.")

    def record_transaction(self, type_, amount):
        self.transaction_history.append({
            'type': type_,
            'amount': amount,
            'timestamp': datetime.datetime.now()
        })

    def get_recent_transactions(self, seconds=60):
        now = datetime.datetime.now()
        return [txn for txn in self.transaction_history if (now - txn['timestamp']).total_seconds() <= seconds]

    def check_suspicious_activity(self):
        recent_txns = self.get_recent_transactions()
        large_transactions = [txn for txn in recent_txns if txn['amount'] > 5000]
        if len(large_transactions) >= 2:
            self.notify("🚨 Suspicious activity: Multiple large transactions in a short period.")

class LowBalanceObserver:
    def __init__(self, threshold=10):
        self.threshold = threshold

    def notify(self, account):
        if account["balance"] < self.threshold:
            messagebox.showwarning("Low Balance", f"Warning: {account['account_type']} balance is low!")

class LoanRepaymentObserver:
    def __init__(self, user):
        self.user = user

    def notify(self):
        import datetime
        today = datetime.date.today()

        alerts = []
        for loan in self.user.get("loans", []):
            due_date_str = loan.get("due_date")
            if due_date_str:
                due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                days_left = (due_date - today).days
                if days_left <= 3:  # Alert if 3 or fewer days remain
                    alerts.append(f"Loan '{loan['loan_type']}' is due in {days_left} day(s) on {due_date}.")

        return alerts
