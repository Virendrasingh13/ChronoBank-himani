# ChronoBank/classes/transactions.py
from ChronoBank.patterns.decorator import TimeTaxDecorator, BonusTimeDecorator

class BasicTransaction:
    def __init__(self, account, amount, is_withdraw=False):
        self.account = account
        self.amount = amount
        self.is_withdraw = is_withdraw

    def execute(self):
        if self.is_withdraw:
            if self.account["balance"] < self.amount:
                raise ValueError("Insufficient balance")
            self.account["balance"] -= self.amount
            print(f"Withdrew {self.amount} time units.")
        else:
            self.account["balance"] += self.amount
            print(f"Deposited {self.amount} time units.")

class TransferTransaction(BasicTransaction):
    def __init__(self, amount):
        self.amount = amount

    def execute(self):
        self.account["balance"] -= self.amount
        print(f"Transferring {self.amount} time units.")

class LoanTransaction(BasicTransaction):
    def __init__(self, amount, duration):
        self.amount = amount
        self.duration = duration

    def execute(self):
        self.account["balance"] -= self.amount
        print(f"Loan of {self.amount} for {self.duration} months.")

class InvestmentTransaction(BasicTransaction):
    def __init__(self, amount, investment_type):
        self.amount = amount
        self.investment_type = investment_type

    def execute(self):
        self.account["balance"] -= self.amount
        print(f"Investing {self.amount} in {self.investment_type}.")
