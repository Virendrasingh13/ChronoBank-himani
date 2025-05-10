# command.py (ChronoBank/command/command.py)

class Command:
    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError


class TransferCommand(Command):
    def __init__(self, from_account, to_account, amount):
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount

    def execute(self):
        self.from_account["balance"] -= self.amount
        self.to_account["balance"] += self.amount

    def undo(self):
        self.from_account["balance"] += self.amount
        self.to_account["balance"] -= self.amount
