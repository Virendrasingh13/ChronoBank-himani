# ChronoBank/classes/account.py
class TimeAccount:
    def __init__(self, account_id, balance=0):
        self.account_id = account_id
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited {amount}, new balance: {self.balance}")

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Withdrew {amount}, new balance: {self.balance}")
        else:
            print("Insufficient funds")

class BasicTimeAccount(TimeAccount):
    def __init__(self, account_id, balance=0):
        self.account_id = account_id
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited {amount}, new balance: {self.balance}")

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Withdrew {amount}, new balance: {self.balance}")
        else:
            print("Insufficient funds")

class InvestorAccount(TimeAccount):
    def __init__(self, account_id, balance=0):
        super().__init__(account_id, balance)

    def invest(self, amount):
        self.balance += amount
        print(f"Invested {amount}, new balance: {self.balance}")

class LoanAccount(TimeAccount):
    def __init__(self, account_id, balance=0):
        super().__init__(account_id, balance)

    def apply_loan(self, amount):
        self.balance += amount
        print(f"Loan applied: {amount}, new balance: {self.balance}")
