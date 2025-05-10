# ChronoBank/patterns/decorator.py
class TransactionDecorator:
    def __init__(self, transaction):
        self.transaction = transaction

    def execute(self):
        self.transaction.execute()

    @property
    def amount(self):
        return self.transaction.amount

    @property
    def account(self):
        return self.transaction.account

class TimeTaxDecorator(TransactionDecorator):
    def execute(self):
        super().execute()
        tax = self.transaction.amount * 0.1  # 10% tax
        self.transaction.account["balance"] -= tax
        print(f"Applying time tax: {tax} units deducted.")

class BonusTimeDecorator(TransactionDecorator):
    def execute(self):
        super().execute()
        bonus = self.transaction.amount * 0.1  # 10% bonus
        self.transaction.account["balance"] += bonus
        print(f"Applying bonus time: {bonus} units added.")

