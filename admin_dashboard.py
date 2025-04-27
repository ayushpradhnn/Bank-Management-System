import tkinter as tk
from tkinter import messagebox
from database import create_connection
from loans import open_loan_management_window
from feedback import open_feedback_management_window 
import mysql.connector

def open_admin_dashboard(admin_id):
    root = tk.Tk()
    root.title("Admin Dashboard")
    root.geometry("500x500")
    root.config(bg="#f7f7f7")

    tk.Label(root, text=f"Welcome Admin (ID: {admin_id})", font=("Arial", 16), bg="#f7f7f7").pack(pady=20)

    # Loan Management
    tk.Button(root, text="Loan Details", width=25, bg="#9C27B0", fg="white",
              command=lambda: open_loan_management_window(admin_id)).pack(pady=10)

    tk.Button(root, text="View and Reply to Feedback", width=25, bg="#607D8B", fg="white",
              command=lambda: open_feedback_management_window(admin_id)).pack(pady=10)

    # Customer Registration
    def open_register_customer_window():
        form = tk.Toplevel(root)
        form.title("Register Customer (Login Credentials)")
        form.geometry("400x400")

        tk.Label(form, text="Email").pack(pady=2)
        email_entry = tk.Entry(form, width=40)
        email_entry.pack()

        tk.Label(form, text="Password").pack(pady=2)
        password_entry = tk.Entry(form, width=40, show="*")
        password_entry.pack()

        tk.Label(form, text="Branch ID").pack(pady=2)
        branch_entry = tk.Entry(form, width=40)
        branch_entry.pack()

        tk.Label(form, text="Account Type").pack(pady=2)
        account_type_var = tk.StringVar(form)
        account_type_var.set("Savings")
        tk.OptionMenu(form, account_type_var, "Savings", "Current", "Fixed Deposit").pack(pady=5)

        def register_customer():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            branch_id = branch_entry.get().strip()
            account_type = account_type_var.get()

            if not all([email, password, branch_id]):
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO customeraccounts(email, password, branchID, accountType)
                    VALUES (%s, %s, %s, %s)
                """, (email, password, branch_id, account_type))

                customer_id = cursor.lastrowid

                if not customer_id:
                    raise Exception("Failed to get customer ID after insert.")

                cursor.execute("""
                    INSERT INTO login(email, password, role, user_ref)
                    VALUES (%s, %s, 'user', %s)
                """, (email, password, customer_id))

                conn.commit()
                messagebox.showinfo("Success", "Customer registered successfully.")
                form.destroy()

            except mysql.connector.Error as err:
                conn.rollback()
                messagebox.showerror("Database Error", str(err))

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))

            finally:
                cursor.close()
                conn.close()

        tk.Button(form, text="Register Customer", command=register_customer, bg="#4CAF50", fg="white").pack(pady=20)

    # Register Customer Button
    tk.Button(root, text="Register Customer", width=25, bg="#2196F3", fg="white",
              command=open_register_customer_window).pack(pady=10)

    # Logout Button
    tk.Button(root, text="Logout", width=25, bg="#F44336", fg="white", command=root.destroy).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    open_admin_dashboard(admin_id=1)  # Replace with dynamic ID
