import tkinter as tk
from tkinter import messagebox
from database import  create_connection
import mysql.connector

def validate_login(email, password):
    conn = create_connection()
    if not conn:
        messagebox.showerror("Error", "Failed to connect to the database.")
        return

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM login WHERE email = %s AND password = %s
        """, (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            role = user['role']
            if role == 'admin':
                messagebox.showinfo("Success", "Admin login successful.")
                import admin_dashboard
                admin_dashboard.open_admin_dashboard(user['admin_ref'])
            else:
                messagebox.showinfo("Success", "User login successful.")
                user_id = user['user_ref']  # Retrieve the customer ID from the login table
                import user_dashboard
                user_dashboard.open_user_dashboard(user_id)  # Open user dashboard and pass the customer ID
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))


def login_screen():
    root = tk.Tk()
    root.title("Banking System Login")
    root.geometry("400x300")
    root.resizable(False, False)

    tk.Label(root, text="Login", font=("Bauhaus 93", 40)).pack(pady=20)

    tk.Label(root, text="Email").pack()
    email_entry = tk.Entry(root, width=30)
    email_entry.pack(pady=5)

    tk.Label(root, text="Password").pack()
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack(pady=5)

    def on_login():
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        if not email or not password:
            messagebox.showwarning("Input Error", "Both fields are required.")
        else:
            validate_login(email, password)

    tk.Button(root, text="Login", command=on_login, bg="#4CAF50", fg="white", width=15).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    login_screen()
