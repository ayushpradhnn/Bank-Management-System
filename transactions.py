import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import create_connection
import mysql.connector

# Deposit Feature
def deposit(user_id, amount):
    try:
        # Check if the amount is valid
        if amount <= 0:
            messagebox.showerror("Error", "Deposit amount must be greater than zero.")
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Step 1: Fetch the current balance
        cursor.execute("SELECT balance FROM customeraccounts WHERE id = %s", (user_id,))
        current_balance = cursor.fetchone()

        if current_balance is None:
            messagebox.showerror("Error", "Customer not found.")
            return

        # Debugging: Log the current balance
        print(f"Current balance for user {user_id}: {current_balance[0]}")

        # If the balance is None (meaning no balance has been set yet), set it to 0.0
        current_balance = current_balance[0] if current_balance[0] is not None else 0.0

        # Calculate the new balance after deposit
        new_balance = current_balance + amount
        print(f"New balance after deposit: {new_balance}")

        # Step 2: Update the balance in the customer account
        cursor.execute("""
            UPDATE customeraccounts
            SET balance = %s
            WHERE id = %s
        """, (new_balance, user_id))

        # Step 3: Insert the transaction into the transactions table
        cursor.execute("""
            INSERT INTO transactions (userId, transactionType, amount, balanceAfter)
            VALUES (%s, 'Deposit', %s, %s)
        """, (user_id, amount, new_balance))

        conn.commit()
        
        # Debugging: Log the success of the transaction
        print(f"Deposit successful for user {user_id}. Amount: {amount}, New Balance: {new_balance}")
        
        messagebox.showinfo("Success", f"Deposited {amount} successfully. New Balance: {new_balance}")

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()


# Withdraw Feature
def withdraw(user_id, amount):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Step 1: Fetch the current balance
        cursor.execute("SELECT balance FROM customeraccounts WHERE id = %s", (user_id,))
        current_balance = cursor.fetchone()
        if not current_balance:
            messagebox.showerror("Error", "Customer not found.")
            return

        if current_balance[0] < amount:
            messagebox.showerror("Error", "Insufficient funds.")
            return

        new_balance = current_balance[0] - amount  # Deduct withdrawal amount from current balance

        # Step 2: Update the balance in the customer account
        cursor.execute(""" 
            UPDATE customeraccounts 
            SET balance = %s 
            WHERE id = %s 
        """, (new_balance, user_id))

        # Step 3: Insert the transaction into the transactions table
        cursor.execute("""
            INSERT INTO transactions (userId, transactionType, amount, balanceAfter) 
            VALUES (%s, 'Withdrawal', %s, %s)
        """, (user_id, amount, new_balance))

        conn.commit()
        messagebox.showinfo("Success", f"Withdrawn {amount} successfully. New Balance: {new_balance}")

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()

# Transfer Feature
def transfer(sender_user_id, recipient_user_id, amount):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Step 1: Fetch the sender's current balance
        cursor.execute("SELECT balance FROM customeraccounts WHERE id = %s", (sender_user_id,))
        sender_balance = cursor.fetchone()
        if not sender_balance:
            messagebox.showerror("Error", "Sender not found.")
            return

        if sender_balance[0] < amount:
            messagebox.showerror("Error", "Insufficient funds.")
            return

        # Step 2: Fetch the recipient's current balance
        cursor.execute("SELECT balance FROM customeraccounts WHERE id = %s", (recipient_user_id,))
        recipient_balance = cursor.fetchone()
        if not recipient_balance:
            messagebox.showerror("Error", "Recipient not found.")
            return

        new_sender_balance = sender_balance[0] - amount
        new_recipient_balance = recipient_balance[0] + amount

        # Step 3: Update balances for both sender and recipient
        cursor.execute(""" 
            UPDATE customeraccounts 
            SET balance = %s 
            WHERE id = %s 
        """, (new_sender_balance, sender_user_id))

        cursor.execute(""" 
            UPDATE customeraccounts 
            SET balance = %s 
            WHERE id = %s 
        """, (new_recipient_balance, recipient_user_id))

        # Step 4: Insert the transactions into the transactions table
        cursor.execute("""
            INSERT INTO transactions (userId, transactionType, amount, balanceAfter, recipientUserId)
            VALUES (%s, 'Transfer', %s, %s, %s)
        """, (sender_user_id, amount, new_sender_balance, recipient_user_id))

        cursor.execute("""
            INSERT INTO transactions (userId, transactionType, amount, balanceAfter, recipientUserId)
            VALUES (%s, 'Transfer', %s, %s, %s)
        """, (recipient_user_id, amount, new_recipient_balance, sender_user_id))

        conn.commit()
        messagebox.showinfo("Success", f"Transferred {amount} successfully.")

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()

# View Balance Feature
def view_balance(user_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Fetch the current balance
        cursor.execute("SELECT balance FROM customeraccounts WHERE id = %s", (user_id,))
        balance = cursor.fetchone()

        if balance:
            messagebox.showinfo("Balance", f"Your current balance is {balance[0]}")
        else:
            messagebox.showerror("Error", "Customer not found.")

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()

# Transaction History Feature
def view_transaction_history(user_id):
    history_window = tk.Toplevel()
    history_window.title("Transaction History")
    history_window.geometry("600x400")
    history_window.config(bg="#f7f7f7")

    tk.Label(history_window, text="Transaction History", font=("Arial", 16), bg="#f7f7f7").pack(pady=20)

    tree = ttk.Treeview(history_window, columns=("ID", "Type", "Amount", "Balance After", "Recipient ID", "Date"), show="headings")
    tree.heading("ID", text="Transaction ID")
    tree.heading("Type", text="Transaction Type")
    tree.heading("Amount", text="Amount")
    tree.heading("Balance After", text="Balance After")
    tree.heading("Recipient ID", text="Recipient User ID")
    tree.heading("Date", text="Transaction Date")
    tree.pack(fill=tk.BOTH, expand=True)

    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE userId = %s
            ORDER BY transactionDate DESC
        """, (user_id,))
        transactions = cursor.fetchall()

        for transaction in transactions:
            tree.insert("", "end", values=(
                transaction["transactionId"],
                transaction["transactionType"],
                transaction["amount"],
                transaction["balanceAfter"],
                transaction["recipientUserId"] or "N/A",
                transaction["transactionDate"]
            ))

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))

    finally:
        cursor.close()
        conn.close()

    tk.Button(history_window, text="Close", command=history_window.destroy, bg="#F44336", fg="white").pack(pady=10)

# Function to open the transactions window and include options like deposit, withdraw, transfer, etc.
def open_transactions_window(user_id):
    transactions_window = tk.Toplevel()
    transactions_window.title("Transactions")
    transactions_window.geometry("500x400")
    transactions_window.config(bg="#f7f7f7")

    tk.Label(transactions_window, text="Transactions", font=("Arial", 16), bg="#f7f7f7").pack(pady=20)

    def open_deposit_window():
        form = tk.Toplevel(transactions_window)
        form.title("Deposit")
        form.geometry("400x300")

        tk.Label(form, text="Amount to Deposit").pack(pady=10)
        deposit_amount_entry = tk.Entry(form, width=40)
        deposit_amount_entry.pack(pady=5)

        def on_deposit():
            try:
                deposit_amount = float(deposit_amount_entry.get().strip())
                if deposit_amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0.")
                    return
                deposit(user_id, deposit_amount)
                form.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount entered.")

        tk.Button(form, text="Deposit", command=on_deposit, bg="#4CAF50", fg="white").pack(pady=20)

    def open_withdraw_window():
        form = tk.Toplevel(transactions_window)
        form.title("Withdraw")
        form.geometry("400x300")

        tk.Label(form, text="Amount to Withdraw").pack(pady=10)
        withdraw_amount_entry = tk.Entry(form, width=40)
        withdraw_amount_entry.pack(pady=5)

        def on_withdraw():
            try:
                withdraw_amount = float(withdraw_amount_entry.get().strip())
                if withdraw_amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0.")
                    return
                withdraw(user_id, withdraw_amount)
                form.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount entered.")

        tk.Button(form, text="Withdraw", command=on_withdraw, bg="#F44336", fg="white").pack(pady=20)

    def open_transfer_window():
        form = tk.Toplevel(transactions_window)
        form.title("Transfer")
        form.geometry("400x300")

        tk.Label(form, text="Recipient User ID").pack(pady=10)
        recipient_user_entry = tk.Entry(form, width=40)
        recipient_user_entry.pack(pady=5)

        tk.Label(form, text="Amount to Transfer").pack(pady=10)
        transfer_amount_entry = tk.Entry(form, width=40)
        transfer_amount_entry.pack(pady=5)

        def on_transfer():
            try:
                recipient_user_id = recipient_user_entry.get().strip()
                transfer_amount = float(transfer_amount_entry.get().strip())
                if transfer_amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0.")
                    return
                transfer(user_id, recipient_user_id, transfer_amount)
                form.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input entered.")

        tk.Button(form, text="Transfer", command=on_transfer, bg="#2196F3", fg="white").pack(pady=20)

    def open_balance_window():
        view_balance(user_id)

    def open_history_window():
        view_transaction_history(user_id)

    # Add buttons for deposit, withdraw, transfer, view balance, transaction history
    tk.Button(transactions_window, text="Deposit", command=open_deposit_window, bg="#4CAF50", fg="white").pack(pady=10)
    tk.Button(transactions_window, text="Withdraw", command=open_withdraw_window, bg="#F44336", fg="white").pack(pady=10)
    tk.Button(transactions_window, text="Transfer", command=open_transfer_window, bg="#2196F3", fg="white").pack(pady=10)
    tk.Button(transactions_window, text="View Balance", command=open_balance_window, bg="#FFC107", fg="white").pack(pady=10)
    tk.Button(transactions_window, text="Transaction History", command=open_history_window, bg="#9C27B0", fg="white").pack(pady=10)

    tk.Button(transactions_window, text="Close", command=transactions_window.destroy, bg="#F44336", fg="white").pack(pady=20)
