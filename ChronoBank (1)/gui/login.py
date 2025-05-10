# gui/login.py
import tkinter as tk
from tkinter import messagebox
import json
import os
from gui.dashboard import Dashboard

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')

class LoginScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ChronoBank Login")
        self.root.geometry("350x250")

        tk.Label(self.root, text="ChronoBank Login", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        self.root.mainloop()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            with open(DB_PATH, "r") as f:
                data = json.load(f)
                for user in data["users"]:
                    if user["username"] == username and user["password"] == password:
                        messagebox.showinfo("Login Successful", f"Welcome {user['name']}!")
                        self.root.destroy()
                        Dashboard(user)  # Pass user info to Dashboard
                        return
        except FileNotFoundError:
            messagebox.showerror("Error", "Database not found.")
            print("Looking for DB at:", DB_PATH)
        except Exception as e:
            messagebox.showerror("Error", str(e))

        messagebox.showerror("Login Failed", "Invalid username or password.")
