from ChronoBank.state.state import ActiveState  # Import your default state

class TimeAccountBuilder:
    def __init__(self):
        self.account = TimeAccount()

    def set_account_type(self, account_type):
        self.account.account_type = account_type
        return self

    def set_interest_rate(self, rate):
        self.account.interest_rate = rate   
        return self

    def set_transaction_limit(self, limit):
        self.account.transaction_limit = limit
        return self
    
    def set_state(self, state):
        self.account.set_state(state)
        return self

    def build(self):
        return self.account

class TimeAccount:
    def __init__(self):
        self.account_type = None
        self.interest_rate = 0
        self.transaction_limit = 0
        self.state = ActiveState()  # Default state

    def __str__(self):
        return f"Account Type: {self.account_type}, Interest Rate: {self.interest_rate}%, Transaction Limit: {self.transaction_limit}"
    
    def set_state(self, state):
        self.state = state

    def apply_state(self):
        self.state.handle(self)
