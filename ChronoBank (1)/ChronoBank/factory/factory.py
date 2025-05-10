# factory.py (Inside `ChronoBank/factory`)

from ChronoBank.classes.account import BasicTimeAccount, InvestorAccount, LoanAccount

class AccountFactory:
    @staticmethod
    def create_account(account_type, account_id, balance=0):
        if account_type == "BasicTimeAccount":
            return BasicTimeAccount(account_id, balance)
        elif account_type == "InvestorAccount":
            return InvestorAccount(account_id, balance)
        elif account_type == "LoanAccount":
            return LoanAccount(account_id, balance)
        else:
            raise ValueError("Unknown account type")
