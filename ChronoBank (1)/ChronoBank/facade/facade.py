# facade.py (Inside `ChronoBank/facade`)

from factory import AccountFactory
from ChronoBank.classes.ledger import Ledger

class ChronoBankFacade:
    def __init__(self):
        self.ledger = Ledger()

    def create_account(self, account_type, account_id, balance=0):
        account = AccountFactory.create_account(account_type, account_id, balance)
        self.ledger.add_transaction(f"Created {account_type} account: {account_id}")
        return account

    def transfer_time(self, from_account, to_account, amount):
        from_account.withdraw(amount)
        to_account.deposit(amount)
        self.ledger.add_transaction(f"Transferred {amount} from {from_account.account_id} to {to_account.account_id}")
