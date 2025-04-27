import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import create_connection
from loans import open_loan_application_window, open_loan_status_window
from feedback import open_feedback_window, open_feedback_status_window
import transactions  # Assuming you have a separate transactions file for transaction logic

def open_user_dashboard(user_id):
    root = tk.Tk()
    root.title("Customer Dashboard")
    root.geometry("500x600")
    root.config(bg="#f7f7f7")

    tk.Label(root, text=f"Welcome User (ID: {user_id})", font=("Arial", 16), bg="#f7f7f7").pack(pady=20)

    # Loan Application
    tk.Button(root, text="Apply for Loan", width=25, bg="#009688", fg="white",
              command=lambda: open_loan_application_window(user_id)).pack(pady=5)

    # View Loan Status
    tk.Button(root, text="View Loan Status", width=25, bg="#3F51B5", fg="white",
              command=lambda: open_loan_status_window(user_id)).pack(pady=5)

    # Submit Feedback
    tk.Button(root, text="Submit Feedback", width=25, bg="#607D8B", fg="white",
              command=lambda: open_feedback_window(user_id)).pack(pady=5)

    # View Feedback Status
    tk.Button(root, text="View Feedback Status", width=25, bg="#607D8B", fg="white",
              command=lambda: open_feedback_status_window(user_id)).pack(pady=5)

    # Update Personal Details
    def open_update_personal_details_window():
        form = tk.Toplevel(root)
        form.title("Update Personal Details")
        form.geometry("400x400")

        tk.Label(form, text="Name").pack(pady=2)
        name_entry = tk.Entry(form, width=40)
        name_entry.pack()

        tk.Label(form, text="Phone").pack(pady=2)
        phone_entry = tk.Entry(form, width=40)
        phone_entry.pack()

        tk.Label(form, text="City").pack(pady=2)
        city_entry = tk.Entry(form, width=40)
        city_entry.pack()

        tk.Label(form, text="Address").pack(pady=2)
        address_entry = tk.Entry(form, width=40)
        address_entry.pack()

        def update_personal_details():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            city = city_entry.get().strip()
            address = address_entry.get().strip()

            if not all([name, phone, city, address]):
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                conn = create_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE customeraccounts
                    SET name = %s, phone = %s, city = %s, address = %s
                    WHERE id = %s
                """, (name, phone, city, address, user_id))

                conn.commit()
                messagebox.showinfo("Success", "Personal details updated successfully.")
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

        tk.Button(form, text="Update Personal Details", command=update_personal_details, bg="#4CAF50", fg="white").pack(pady=20)

    # View Personal Details
    def open_view_personal_details_window():
        form = tk.Toplevel(root)
        form.title("View Personal Details")
        form.geometry("400x300")

        try:
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT name, phone, city, address FROM customeraccounts WHERE id = %s
            """, (user_id,))
            user_details = cursor.fetchone()

            if user_details:
                tk.Label(form, text=f"Name: {user_details['name']}", font=("Arial", 12)).pack(pady=10)
                tk.Label(form, text=f"Phone: {user_details['phone']}", font=("Arial", 12)).pack(pady=10)
                tk.Label(form, text=f"City: {user_details['city']}", font=("Arial", 12)).pack(pady=10)
                tk.Label(form, text=f"Address: {user_details['address']}", font=("Arial", 12)).pack(pady=10)
            else:
                messagebox.showerror("Error", "Could not retrieve personal details.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            conn.close()

    tk.Button(root, text="Update Personal Details", width=25, bg="#2196F3", fg="white",
              command=open_update_personal_details_window).pack(pady=10)

    tk.Button(root, text="View Personal Details", width=25, bg="#2196F3", fg="white",
              command=open_view_personal_details_window).pack(pady=10)

    # Transactions
    def open_transaction_window():
        transactions.open_transactions_window(user_id)

    tk.Button(root, text="Transactions", width=25, bg="#2196F3", fg="white",
              command=open_transaction_window).pack(pady=10)

    # Logout
    tk.Button(root, text="Logout", width=25, bg="#F44336", fg="white", command=root.destroy).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    open_user_dashboard(user_id=1)  # Replace 1 with dynamic value as needed
