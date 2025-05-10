import tkinter as tk
from tkinter import messagebox, simpledialog
from ChronoBank.factory.factory import AccountFactory
from ChronoBank.classes.account import BasicTimeAccount, InvestorAccount, LoanAccount
from ChronoBank.strategy.strategy import LoanRepaymentStrategy, LoanApprovalStrategy
from ChronoBank.classes.adapter import LegacyBankSystem, TimeAccountAdapter
from ChronoBank.classes.ledger import Ledger
from ChronoBank.classes.transactions import BasicTransaction
from ChronoBank.patterns.decorator import BonusTimeDecorator, TimeTaxDecorator
from ChronoBank.classes.observer import UserNotification, LowBalanceObserver
from ChronoBank.classes.fraud import FraudDetector
from ChronoBank.command.command import TransferCommand, Command
from ChronoBank.security.reputation import ReputationManager
from ChronoBank.state.state_manager import StateManager

import json
import os
import uuid  # Import uuid for generating unique IDs

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')  # Path to db.json

class Dashboard:
    def __init__(self, user_data):
        self.user = user_data
        self.root = tk.Tk()
        self.root.title("ChronoBank Dashboard")
        self.root.geometry("500x400")
        self.last_command = None
        Ledger().load_user_transactions(self.user["user_id"])
        
        self.observer = UserNotification(user_data)
        self.fraud_detector = FraudDetector()
        self.reputation_manager = ReputationManager()


        # Displaying user info
        tk.Label(self.root, text=f"Welcome, {self.user['name']}", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text=f"User ID: {self.user['user_id']}", font=("Arial", 10)).pack()
        
        
        # Show the accounts
        tk.Label(self.root, text="Accounts:", font=("Arial", 12, "bold")).pack(pady=5)
        self.account_labels = []
        self.account_frame = tk.Frame(self.root)  # Create a frame to hold account labels
        self.account_frame.pack()
        self.refresh_account_display()  # Initial display of accounts


        # Buttons for operations
        tk.Button(self.root, text="Add New Account", command=self.add_account).pack(pady=5)
        tk.Button(self.root, text="Transfer Time", command=self.transfer_time).pack(pady=5)
        tk.Button(self.root, text="Undo Last Transfer", command=self.undo_last_transfer).pack(pady=5)
        tk.Button(self.root, text="View Balance", command=self.view_balance).pack(pady=5)
        tk.Button(self.root, text="View Reputation and Risk Score", command=self.view_reputation).pack(pady=5)
        tk.Button(self.root, text="Deposit Time", command=self.deposit_time).pack(pady=5)
        tk.Button(self.root, text="Withdraw Time", command=self.withdraw_time).pack(pady=5)
        tk.Button(self.root, text="Transaction History", command=self.view_transaction_history).pack(pady=5)
        tk.Button(self.root, text="Apply for Loan", command=self.apply_for_loan).pack(pady=5)
        tk.Button(self.root, text="Repay Loan", command=self.repay_loan).pack(pady=5)
        tk.Button(self.root, text="Invest Time", command=self.invest_time).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=20)

        self.root.mainloop()

    def view_reputation(self):
        reputation = self.user.get("reputation", "N/A")
        risk_score = self.user.get("risk_score", "N/A")
        messagebox.showinfo("User Reputation",f"Reputation: {reputation}\nRisk Score: {risk_score}")

    def refresh_account_display(self):
        """ Refresh the account display to show current accounts """
        # Clear existing account labels
        for label in self.account_labels:
            label.destroy()
        self.account_labels.clear()  # Clear the list of labels
        # Display updated account information
        for acc in self.user["accounts"]:
            label = tk.Label(self.account_frame, text=f"{acc['account_type']} — Balance: {acc['balance']:.2f} time units")
            self.account_labels.append(label)
            label.pack() 

    def add_account(self):
        from ChronoBank.patterns.builder import TimeAccountBuilder

        account_type = simpledialog.askstring("Account Type", "Enter account type (Basic, Investor, Loan):")
        if account_type not in ['Basic', 'Investor', 'Loan']:
            messagebox.showerror("Error", "Invalid account type selected. Please enter Basic, Investor, or Loan.")
            return

        balance = simpledialog.askfloat("Initial Balance", "Enter initial balance:")
        if balance is None:
            return

        # Correct mapping from user input to factory-compatible class names
        type_mapping = {
            "Basic": "BasicTimeAccount",
            "Investor": "InvestorAccount",
            "Loan": "LoanAccount"
        }

        account_class_name = type_mapping[account_type]  # Map to factory class name
        account_factory = AccountFactory()
        account_id = str(uuid.uuid4())
        new_account = account_factory.create_account(account_class_name, account_id, balance)

        # Optional Builder Configuration
        builder = TimeAccountBuilder().set_account_type(account_class_name)
        interest_rate = simpledialog.askfloat("Interest Rate (optional)", "Enter interest rate (%), or leave blank:")
        limit = simpledialog.askinteger("Transaction Limit (optional)", "Enter transaction limit, or leave blank:")
        if interest_rate is not None:
            builder.set_interest_rate(interest_rate)
        if limit is not None:
            builder.set_transaction_limit(limit)
        built_account_config = builder.build()
        print("Builder Config:", built_account_config)

        from ChronoBank.state.state import ActiveState

        # Add account to user list with state info
        self.user["accounts"].append({
            "account_id": new_account.account_id,
            "account_type": new_account.__class__.__name__,
            "balance": new_account.balance,
            "state": "Active"  # Default state name (string-based)
        })

        messagebox.showinfo("Account Added", f"New {new_account.__class__.__name__} account added!")
        self.save_to_db()
        self.refresh_account_display()

    def save_to_db(self):
        """ Save the current user data to db.json """
        try:
            with open(DB_PATH, "r") as f:
                data = json.load(f)

            # Update the user data in the database
            for user in data["users"]:
                if user["user_id"] == self.user["user_id"]:
                    user["accounts"] = self.user["accounts"]
                    user["reputation"] = self.user.get("reputation", 50)
                    user["risk_score"] = self.user.get("risk_score", 50)
                    break

            # Write the updated data back to db.json
            with open(DB_PATH, "w") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def apply_for_loan(self):
        """ Apply for a loan using strategy pattern and custom amount """
        from ChronoBank.strategy.strategy import LoanApprovalStrategy
        from ChronoBank.classes.account import LoanAccount
        from ChronoBank.classes.ledger import Ledger

        # Ask loan type
        loan_type = messagebox.askquestion("Loan Type", "Choose loan type:\nYes for Short-term\nNo for Long-term")
        loan_strategy = LoanApprovalStrategy()
        loan_strategy.set_strategy('Fixed' if loan_type == 'yes' else 'Dynamic')

        # Ask loan amount
        loan_amount = simpledialog.askfloat("Loan Amount", "Enter loan amount:")
        if loan_amount is None or loan_amount <= 0:
            messagebox.showerror("Error", "Invalid loan amount.")
            return

        # Create and approve loan
        loan_account = LoanAccount(account_id="L001")  # Replace with dynamic ID if needed
        loan_strategy.approve_loan(loan_account, loan_amount)

        # Add or update in user accounts
        existing_loan = next((acc for acc in self.user["accounts"] if acc["account_type"] == "LoanAccount"), None)
        if existing_loan:
            existing_loan["balance"] += loan_account.balance
        else:
            self.user["accounts"].append({
                "account_id": loan_account.account_id,
                "account_type": "LoanAccount",
                "balance": loan_account.balance
            })

        # Record in ledger
        Ledger().add_transaction({
            "type": "Loan Approved",
            "amount": loan_amount,
            "to_account": "LoanAccount",
            "strategy": 'Fixed' if loan_type == 'yes' else 'Dynamic'
        })

        self.save_to_db()
        self.refresh_account_display()
        messagebox.showinfo("Loan Approved", f"A loan of {loan_amount} time units was granted.")


    def repay_loan(self):
        """ Repay a loan and deduct from selected account """
        from ChronoBank.strategy.strategy import LoanApprovalStrategy
        from ChronoBank.classes.account import LoanAccount
        from ChronoBank.classes.ledger import Ledger

        # Find loan account
        loan_data = next((acc for acc in self.user["accounts"] if acc["account_type"] == "LoanAccount"), None)
        if not loan_data or loan_data["balance"] <= 0:
            messagebox.showerror("Error", "No active loan account found.")
            return

        # Ask repayment strategy
        strategy_type = messagebox.askquestion("Repayment Type", "Choose repayment type:\nYes for Fixed\nNo for Dynamic")
        loan_strategy = LoanApprovalStrategy()
        loan_strategy.set_strategy('Fixed' if strategy_type == 'yes' else 'Dynamic')

        loan_account = LoanAccount(account_id=loan_data["account_id"], balance=loan_data["balance"])
        repayment_amount = loan_strategy.calculate_repayment(loan_account)

        # Ask which account to deduct from
        account_types = [f"{i}: {acc['account_type']} — Balance: {acc['balance']}" 
                        for i, acc in enumerate(self.user["accounts"]) if acc["account_type"] != "LoanAccount"]
        if not account_types:
            messagebox.showerror("Error", "No source account to deduct from.")
            return

        deduction_index = simpledialog.askinteger("Select Account",
                                                "Select account number to deduct from:\n" + "\n".join(account_types))
        if deduction_index is None or deduction_index < 0 or deduction_index >= len(self.user["accounts"]):
            messagebox.showerror("Error", "Invalid account selection.")
            return

        source_account = self.user["accounts"][deduction_index]

        if source_account["balance"] < repayment_amount:
            messagebox.showerror("Error", "Insufficient balance to repay the loan.")
            self.reputation_manager.adjust_reputation(self.user, -3,  self.save_to_db)
            self.save_to_db()
            return

        # Deduct and update
        source_account["balance"] -= repayment_amount
        loan_account.balance -= repayment_amount
        loan_data["balance"] = loan_account.balance
        self.reputation_manager.adjust_reputation(self.user, +2,  self.save_to_db)

        # Record transaction
        Ledger().add_transaction({
            "type": "Loan Repayment",
            "amount": repayment_amount,
            "from_account": source_account["account_type"],
            "to_account": "LoanAccount",
            "strategy": 'Fixed' if strategy_type == 'yes' else 'Dynamic'
        })

        self.save_to_db()
        self.refresh_account_display()
        messagebox.showinfo("Repayment Complete", f"{repayment_amount} repaid from {source_account['account_type']}.")


    def invest_time(self):
        """Invest time into an InvestAccount with a dynamic interest rate and maturity date."""

        import random
        import datetime
        from ChronoBank.classes.ledger import Ledger

        invest_amount = simpledialog.askfloat("Investment", "Enter time units to invest:")
        if invest_amount is None or invest_amount <= 0:
            messagebox.showerror("Error", "Invalid investment amount.")
            return

        invest_account = next((acc for acc in self.user["accounts"] if acc["account_type"] == "InvestorAccount"), None)
        if not invest_account:
            invest_account = {
                "account_id": "IA001",  # you can generate dynamic IDs if needed
                "account_type": "InvestorAccount",
                "balance": 0
            }
            self.user["accounts"].append(invest_account)

        source_options = [
            (i, acc) for i, acc in enumerate(self.user["accounts"])
            if acc["account_type"] not in ["InvestorAccount", "LoanAccount"]
        ]
        if not source_options:
            messagebox.showerror("Error", "No account available to fund investment.")
            return

        options_str = "\n".join(f"{i}: {acc['account_type']} — Balance: {acc['balance']}" for i, acc in source_options)
        choice = simpledialog.askinteger("Select Account", "Choose account to invest from:\n" + options_str)
        if choice is None or not any(i == choice for i, _ in source_options):
            messagebox.showerror("Error", "Invalid selection.")
            return

        selected_acc = dict(source_options)[choice]
        if selected_acc["balance"] < invest_amount:
            messagebox.showerror("Error", "Insufficient balance in selected account.")
            return

        # Step 4: Deduct from selected account
        selected_acc["balance"] -= invest_amount


        # Step 5: Simulate dynamic interest and store maturity date
        interest_rate = round(random.uniform(0.03, 0.09), 4)  # 3%–9% interest
        interest_earned = round(invest_amount * interest_rate, 2)
        maturity_date = str(datetime.date.today() + datetime.timedelta(days=7))

        # Step 6: Add invested amount to InvestAccount balance (optional)
        invest_account["balance"] += invest_amount

        # Step 7: Store in user["investments"]
        if "investments" not in self.user:
            self.user["investments"] = []

        self.user["investments"].append({
            "amount": invest_amount,
            "interest_rate": interest_rate,
            "interest_earned": interest_earned,
            "invested_on": str(datetime.date.today()),
            "maturity_date": maturity_date,
            "status": "Active"
        })

        # Step 8: Ledger record
        Ledger().add_transaction({
            "type": "Investment",
            "amount": invest_amount,
            "interest_rate": interest_rate,
            "from_account": selected_acc["account_type"],
            "to_account": "InvestAccount",
            "maturity_date": maturity_date
        })

        self.save_to_db()
        self.refresh_account_display()
        messagebox.showinfo(
            "Investment Successful",
            f"Invested {invest_amount} at {interest_rate*100:.2f}% interest.\n"
            f"Matures on {maturity_date} with {interest_earned} interest."
        )


    def view_balance(self):
        """ View the balance for each of the user's accounts """
        self.refresh_account_display()

        StateManager.force_state_evaluation()
        balance_message = "Account Balances:\n"
        for acc in self.user["accounts"]:
            # Check if acc is a dictionary and access its keys
            if isinstance(acc, dict):
                balance_message += f"{acc['account_type']} — Balance: {acc['balance']:.2f} time units — State: {acc['state']}\n"
            else:
                # If acc is an instance of a class, access its attributes
                balance_message += f"{acc.__class__.__name__} — Balance: {acc.balance} time units — State: {acc.state}\n"

        messagebox.showinfo("Account Balances", balance_message)


    def logout(self):
        self.root.destroy()
        from gui.login import LoginScreen  # Import moved here to avoid circular import
        LoginScreen()

    def transfer_time(self):
        from ChronoBank.security.reputation import ReputationManager

        if not ReputationManager.can_make_high_risk_transaction(self.user):
            messagebox.showerror("Access Denied", "Your reputation or risk score does not permit this transaction.")
            return
        
        transfer_window = tk.Toplevel(self.root)
        transfer_window.title("Transfer Time")
        transfer_window.geometry("400x300")

        tk.Label(transfer_window, text="Select From Account:").pack(pady=5)
        from_var = tk.StringVar()
        from_options = [f"{i}: {acc['account_type']} (Balance: {acc['balance']})" for i, acc in enumerate(self.user["accounts"])]
        from_menu = tk.OptionMenu(transfer_window, from_var, *from_options)
        from_menu.pack()

        tk.Label(transfer_window, text="Select To Account:").pack(pady=5)
        to_var = tk.StringVar()
        to_options = [f"{i}: {acc['account_type']} (Balance: {acc['balance']})" for i, acc in enumerate(self.user["accounts"])]
        to_menu = tk.OptionMenu(transfer_window, to_var, *to_options)
        to_menu.pack()

        tk.Label(transfer_window, text="Amount to Transfer:").pack(pady=5)
        amount_entry = tk.Entry(transfer_window)
        amount_entry.pack()

        def execute_transfer():
            try:
                from_index = int(from_var.get().split(":")[0])
                to_index = int(to_var.get().split(":")[0])
                amount = int(amount_entry.get())

                if from_index == to_index:
                    messagebox.showerror("Invalid Transfer", "Cannot transfer to the same account.")
                    return

                from_account = self.user["accounts"][from_index]
                to_account = self.user["accounts"][to_index]

                if from_account["balance"] < amount:
                    messagebox.showerror("Insufficient Funds", "Not enough time units.")
                    self.reputation_manager.adjust_reputation(self.user, -3,  self.save_to_db)
                    self.save_to_db
                    return

                # Use Command pattern
                command = TransferCommand(from_account, to_account, amount)
                command.execute()
                self.last_command = command  # Save for undo

                self.reputation_manager.adjust_reputation(self.user, +2,  self.save_to_db)



                StateManager.force_state_evaluation()

                

                messagebox.showinfo("Success", f"Transferred {amount} time units.")
                Ledger().add_transaction({
                "type": "Transfer",
                "from_account": from_account["account_type"],
                "to_account": to_account["account_type"],
                "amount": amount
                })

                LowBalanceObserver().notify(from_account)

                fraud_result = self.fraud_detector.check_transaction({
                    "type": "Deposit",
                    "amount": amount,
                    "to_account": to_account["account_type"]
                })

                if fraud_result:
                    messagebox.showwarning("Fraud Alert", fraud_result)
                    self.reputation_manager.adjust_reputation(self.user, -5,  self.save_to_db)
                
                self.save_to_db()

                transfer_window.destroy()
                self.refresh_account_display()  # Initial display of accounts

            except Exception as e:
                messagebox.showerror("Transfer Error", str(e))

        tk.Button(transfer_window, text="Transfer", command=execute_transfer).pack(pady=10)

    def view_transaction_history(self):
        ledger = Ledger()
        transactions = ledger.get_transactions()

        if not transactions:
            messagebox.showinfo("Transaction History", "No transactions recorded yet.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Transaction History")
        history_window.geometry("400x300")

        tk.Label(history_window, text="Last 10 Transactions", font=("Arial", 12, "bold")).pack(pady=5)
        text_widget = tk.Text(history_window, wrap="word", height=15)
        text_widget.pack(fill="both", expand=True)

        for i, txn in enumerate(transactions[::-1], 1):  # Show most recent first
            from_acc = txn.get("from_account", "-")
            to_acc = txn.get("to_account", "-")
            amount = round(txn.get("amount", 0), 2)
            entry = f"{i}. {txn['type']} - From: {from_acc}, To: {to_acc}, Amount: {amount} time units\n"
            text_widget.insert(tk.END, entry)



    def deposit_time(self):
        deposit_window = tk.Toplevel(self.root)
        deposit_window.title("Deposit Time")
        deposit_window.geometry("500x400")

        tk.Label(deposit_window, text="Select Account:").pack(pady=5)
        listbox = tk.Listbox(deposit_window)
        listbox.pack()
        for i, acc in enumerate(self.user["accounts"]):
            listbox.insert(tk.END, f"{i}: {acc['account_type']} — Balance: {acc['balance']}")

        tk.Label(deposit_window, text="Enter amount to deposit:").pack(pady=5)
        amount_entry = tk.Entry(deposit_window)
        amount_entry.pack()

        def confirm_deposit():
            try:
                selected = listbox.curselection()
                if not selected:
                    messagebox.showerror("Error", "No account selected")
                    return
                index = int(selected[0])
                amount = float(amount_entry.get())

                #self.user["accounts"][index]["balance"] += amount
                to_account=self.user["accounts"][index]
                # Decorated transaction
                account = self.user["accounts"][index]
                txn = BasicTransaction(account, amount)
                decorated_txn = BonusTimeDecorator(TimeTaxDecorator(txn))
                decorated_txn.execute()

                # Adapter pattern usage
                from ChronoBank.classes.adapter import LegacyBankSystem, TimeAccountAdapter
                adapter = TimeAccountAdapter(LegacyBankSystem())
                adapter.deposit_time(amount)

                self.reputation_manager.adjust_reputation(self.user, +2,  self.save_to_db)


              

                StateManager.force_state_evaluation()

                

                from ChronoBank.classes.ledger import Ledger
                Ledger().add_transaction({
                    "type": "Deposit",
                    "amount": amount,
                    "to_account": self.user["accounts"][index]["account_type"],
                    "decorators": ["TimeTax", "BonusTime"]
                })

                fraud_result = self.fraud_detector.check_transaction({
                    "type": "Deposit",
                    "amount": amount,
                    "to_account": account["account_type"]
                })

                if fraud_result:
                    messagebox.showwarning("Fraud Alert", fraud_result)
                    self.reputation_manager.adjust_reputation(self.user, -5,  self.save_to_db)


                self.save_to_db()
                self.refresh_account_display()
                LowBalanceObserver().notify(account)
                messagebox.showinfo("Success", f"{amount} time units deposited.")
                deposit_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(deposit_window, text="Deposit", command=confirm_deposit).pack(pady=10)
        


    def withdraw_time(self):
        withdraw_window = tk.Toplevel(self.root)
        withdraw_window.title("Withdraw Time")
        withdraw_window.geometry("500x400")

        tk.Label(withdraw_window, text="Select Account:").pack(pady=5)
        listbox = tk.Listbox(withdraw_window)
        listbox.pack()
        for i, acc in enumerate(self.user["accounts"]):
            listbox.insert(tk.END, f"{i}: {acc['account_type']} — Balance: {acc['balance']}")

        tk.Label(withdraw_window, text="Enter amount to withdraw:").pack(pady=5)
        amount_entry = tk.Entry(withdraw_window)
        amount_entry.pack()

        def confirm_withdraw():
            try:
                selected = listbox.curselection()
                if not selected:
                    messagebox.showerror("Error", "No account selected")
                    return
                index = int(selected[0])
                amount = float(amount_entry.get())

                current_balance = self.user["accounts"][index]["balance"]
                if amount > current_balance:
                    messagebox.showerror("Error", "Insufficient balance")
                    self.reputation_manager.adjust_reputation(self.user, -3,  self.save_to_db)
                    return

                #self.user["accounts"][index]["balance"] -= amount
                from_account=self.user["accounts"][index]
                # Decorated transaction
                account = self.user["accounts"][index]
                txn = BasicTransaction(account, amount, is_withdraw=True)
                decorated_txn = BonusTimeDecorator(TimeTaxDecorator(txn))
                decorated_txn.execute()

                # Adapter pattern usage
                from ChronoBank.classes.adapter import LegacyBankSystem, TimeAccountAdapter
                adapter = TimeAccountAdapter(LegacyBankSystem())
                adapter.withdraw_time(amount)

                self.reputation_manager.adjust_reputation(self.user, +2,  self.save_to_db)

                # Wrap from_account and to_account as adapter objects

                
                StateManager.force_state_evaluation()


                from ChronoBank.classes.ledger import Ledger
                Ledger().add_transaction({
                    "type": "Withdraw",
                    "amount": amount,
                    "from_account": self.user["accounts"][index]["account_type"],
                    "decorators": ["TimeTax"]
                })

                fraud_result = self.fraud_detector.check_transaction({
                    "type": "Deposit",
                    "amount": amount,
                    "to_account": account["account_type"]
                })

                if fraud_result:
                    messagebox.showwarning("Fraud Alert", fraud_result)
                    self.reputation_manager.adjust_reputation(self.user, -5,  self.save_to_db)

                self.save_to_db()
                self.refresh_account_display()
                LowBalanceObserver().notify(account)
                messagebox.showinfo("Success", f"{amount} time units withdrawn.")
                withdraw_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(withdraw_window, text="Withdraw", command=confirm_withdraw).pack(pady=10)
        
    def undo_last_transfer(self):
        if self.last_command:
            self.last_command.undo()
            self.save_to_db()
            self.refresh_account_display()
            messagebox.showinfo("Undo Successful", "The last transfer was undone.")
            self.last_command = None
        else:
            messagebox.showwarning("No Action", "No previous transfer to undo.")
