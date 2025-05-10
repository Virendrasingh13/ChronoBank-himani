class AccountState:
    def __init__(self, state_name):
        self.state_name = state_name

    def __str__(self):
        return self.state_name

    @staticmethod
    def evaluate(account_dict):
        balance = float(account_dict.get("balance", 0.0))
        if account_dict.get("fraud"):
            return AccountState("Frozen")
        elif balance <= 0:
            return AccountState("Overdrawn")
        else:
            return AccountState("Active")
