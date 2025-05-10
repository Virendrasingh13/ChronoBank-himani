import os
import json
from ChronoBank.state.state import AccountState

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'db.json')

class StateManager:
    @staticmethod
    def evaluate(account):
        if hasattr(account, 'account_dict'):
            account_dict = account.account_dict
        elif isinstance(account, dict):
            account_dict = account
        else:
            raise TypeError("Unsupported account type for state evaluation")

        new_state = AccountState.evaluate(account_dict)
        print(f"Evaluating account {account_dict.get('account_id')} (balance: {account_dict.get('balance')}) -> New state: {new_state}")

        account_dict["state"] = str(new_state)

        StateManager.save_to_db(account_dict)
        return str(new_state)

    @staticmethod
    def save_to_db(account_dict):
        try:
            with open(DB_PATH, 'r') as f:
                data = json.load(f)
            
            for user in data["users"]:
                for account in user["accounts"]:
                    if account["account_id"] == account_dict["account_id"]:
                        account["state"] = account_dict["state"]
                        print(f"DB: Updated account {account['account_id']} to state {account['state']}")
                        break
            
            with open(DB_PATH, 'w') as f:
                json.dump(data, f, indent=4)
            print("DB: Changes written to db.json")
        except Exception as e:
            print(f"Error saving state to database: {e}")

    @staticmethod
    def force_state_evaluation():
        print("Running force_state_evaluation...")
        try:
            with open(DB_PATH, 'r') as f:
                data = json.load(f)
            
            modified = False
            for user in data["users"]:
                for account in user["accounts"]:
                    old_state = account.get("state")
                    new_state = StateManager.evaluate(account)
                    if old_state != new_state:
                        modified = True
                        print(f"Account {account['account_id']} state changed from {old_state} to {new_state}")
            
            if modified:
                # Write the updated data back to db.json
                with open(DB_PATH, 'w') as f:
                    json.dump(data, f, indent=4)
                print("Database updated with new states")
            else:
                print("No state changes were needed")
        except Exception as e:
            print(f"Error in force state evaluation: {e}")
