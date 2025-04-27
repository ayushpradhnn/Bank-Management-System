import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from database import create_connection

def open_loan_management_window(admin_id):
    window = tk.Toplevel()
    window.title("Loan Management")
    window.geometry("700x500")
    window.config(bg="#f7f7f7")

    tk.Label(window, text="Pending Loan Requests", font=("Arial", 16), bg="#f7f7f7").pack(pady=10)

    tree = ttk.Treeview(window, columns=("loanId", "userId", "loanType", "amount"), show="headings")
    tree.heading("loanId", text="Loan ID")
    tree.heading("userId", text="User ID")
    tree.heading("loanType", text="Loan Type")
    tree.heading("amount", text="Amount")
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def load_pending_loans():
        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT loanId, userId, loanType, amount FROM loans WHERE status = 'Pending'")
            rows = cursor.fetchall()

            for row in rows:
                tree.insert("", "end", values=(row["loanId"], row["userId"], row["loanType"], row["amount"]))

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    def process_selected():
        selected = tree.focus()
        if not selected:
            messagebox.showerror("Error", "No loan selected.")
            return

        values = tree.item(selected, 'values')
        loan_id = values[0]

        process_window = tk.Toplevel(window)
        process_window.title(f"Process Loan ID: {loan_id}")
        process_window.geometry("400x300")

        tk.Label(process_window, text=f"Loan ID: {loan_id}", font=("Arial", 14)).pack(pady=10)

        tk.Label(process_window, text="Set Interest Rate (%):").pack()
        interest_entry = tk.Entry(process_window)
        interest_entry.pack(pady=5)

        def approve():
            try:
                rate = float(interest_entry.get())
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE loans 
                    SET status='Approved', interestRate=%s, adminId=%s
                    WHERE loanId=%s
                """, (rate, admin_id, loan_id))
                conn.commit()
                messagebox.showinfo("Success", f"Loan {loan_id} approved with {rate}% interest.")
                process_window.destroy()
                window.destroy()
                open_loan_management_window(admin_id)  # Refresh
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                cursor.close()
                conn.close()

        def reject():
            try:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE loans 
                    SET status='Rejected', adminId=%s
                    WHERE loanId=%s
                """, (admin_id, loan_id))
                conn.commit()
                messagebox.showinfo("Rejected", f"Loan {loan_id} rejected.")
                process_window.destroy()
                window.destroy()
                open_loan_management_window(admin_id)  # Refresh
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                cursor.close()
                conn.close()

        tk.Button(process_window, text="Approve", command=approve, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(process_window, text="Reject", command=reject, bg="#F44336", fg="white").pack(pady=5)

    tk.Button(window, text="Process Selected Loan", command=process_selected, bg="#2196F3", fg="white").pack(pady=10)
    tk.Button(window, text="Close", command=window.destroy, bg="#F44336", fg="white").pack(pady=10)

    load_pending_loans()

# =========================
# CUSTOMER: APPLY FOR LOAN
# =========================
def open_loan_application_window(user_id):
    form = tk.Toplevel()
    form.title("Apply for Loan")
    form.geometry("400x400")
    form.config(bg="#f7f7f7")

    tk.Label(form, text="Apply for a Loan", font=("Arial", 16), bg="#f7f7f7").pack(pady=15)

    tk.Label(form, text="Loan Type", bg="#f7f7f7").pack()
    loan_type_var = tk.StringVar()
    loan_type_var.set("Personal")
    tk.OptionMenu(form, loan_type_var, "Home", "Personal", "Auto", "Business").pack()

    tk.Label(form, text="Amount", bg="#f7f7f7").pack(pady=5)
    amount_entry = tk.Entry(form)
    amount_entry.pack()

    def submit_application():
        loan_type = loan_type_var.get()
        try:
            amount = float(amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO loans (userId, loanType, amount, status)
                VALUES (%s, %s, %s, 'Pending')
            """, (user_id, loan_type, amount))
            conn.commit()
            messagebox.showinfo("Success", "Loan application submitted!")
            form.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    tk.Button(form, text="Submit Application", bg="#4CAF50", fg="white", command=submit_application).pack(pady=20)

# =========================
# CUSTOMER: VIEW LOAN STATUS
# =========================
def open_loan_status_window(user_id):
    status_window = tk.Toplevel()
    status_window.title("My Loan Applications")
    status_window.geometry("700x400")
    status_window.config(bg="#f7f7f7")

    tk.Label(status_window, text="Loan Status & Interest Rates", font=("Arial", 16), bg="#f7f7f7").pack(pady=10)

    tree = ttk.Treeview(status_window, columns=("ID", "Type", "Amount", "Status", "Interest Rate", "Updated"), show="headings")
    tree.heading("ID", text="Loan ID")
    tree.heading("Type", text="Loan Type")
    tree.heading("Amount", text="Amount")
    tree.heading("Status", text="Status")
    tree.heading("Interest Rate", text="Interest Rate (%)")
    tree.heading("Updated", text="Last Updated")
    tree.pack(fill=tk.BOTH, expand=True)

    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT loanId, loanType, amount, status, interestRate, loanStatusUpdated 
            FROM loans 
            WHERE userId = %s
            ORDER BY loanStatusUpdated DESC
        """, (user_id,))
        loans = cursor.fetchall()

        for loan in loans:
            tree.insert("", "end", values=(
                loan["loanId"],
                loan["loanType"],
                float(loan["amount"]),
                loan["status"],
                loan["interestRate"] if loan["interestRate"] is not None else "N/A",
                loan["loanStatusUpdated"]
            ))

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        cursor.close()
        conn.close()

    tk.Button(status_window, text="Close", command=status_window.destroy, bg="#F44336", fg="white").pack(pady=10)
