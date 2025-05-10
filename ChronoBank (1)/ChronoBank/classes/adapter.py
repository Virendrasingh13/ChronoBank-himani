# ChronoBank/classes/adapter.py

class LegacyBankSystem:
    def deposit_money(self, amount):
        print(f"Deposited {amount} in Legacy Bank.")

    def withdraw_money(self, amount):
        print(f"Withdrew {amount} from Legacy Bank.")

class TimeAccountAdapter:
    def __init__(self, legacy_system):
        self.legacy_system = legacy_system

    def deposit_time(self, amount):
        self.legacy_system.deposit_money(amount)

    def withdraw_time(self, amount):
        self.legacy_system.withdraw_money(amount)

class LegacySystemAdapter:
    def __init__(self, legacy_system):
        self.legacy_system = legacy_system

    def deposit_time(self, amount):
        self.legacy_system.deposit_money(amount)

    def withdraw_time(self, amount):
        self.legacy_system.withdraw_money(amount)