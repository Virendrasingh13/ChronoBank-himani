# ChronoBank/strategy.py

class LoanRepaymentStrategy:
    """ Strategy class for loan repayment """
    def calculate_repayment(self, loan_amount):
        raise NotImplementedError("Subclasses should implement this method.")

class FixedRepaymentStrategy(LoanRepaymentStrategy):
    """ Fixed repayment strategy over 12 months """
    def calculate_repayment(self, loan_amount):
        return loan_amount / 12  # Repayment divided equally over 12 months

class DynamicRepaymentStrategy(LoanRepaymentStrategy):
    """ Dynamic repayment strategy (e.g., 10% of loan amount per month) """
    def calculate_repayment(self, loan_amount):
        return loan_amount * 0.1  # Repayment is 10% of the loan amount each month

class LoanApprovalStrategy:
    """ Strategy class for loan approval """
    def __init__(self):
        self.strategy = None

    def set_strategy(self, strategy_type):
        """ Set the loan repayment strategy type """
        if strategy_type == 'Fixed':
            self.strategy = FixedRepaymentStrategy()
        elif strategy_type == 'Dynamic':
            self.strategy = DynamicRepaymentStrategy()

    def approve_loan(self, loan_account, amount):
        print(f"Loan for account {loan_account.account_id} approved.")
        loan_account.balance = amount
        print(f"Loan of {amount} time units granted.")

    def calculate_repayment(self, loan_account):
        """ Calculate the repayment based on selected strategy """
        if self.strategy:
            repayment = self.strategy.calculate_repayment(loan_account.balance)
            print(f"Monthly repayment for loan account {loan_account.account_id}: {repayment}")
            return repayment
        else:
            print("No repayment strategy selected.")
            return 0
