import tkinter as tk
from tkinter import messagebox
from database import create_connection
import mysql.connector

def open_feedback_window(user_id):
    form = tk.Toplevel()
    form.title("Submit Feedback")
    form.geometry("400x400")

    tk.Label(form, text="Enter your feedback:").pack(pady=10)
    feedback_entry = tk.Text(form, height=10, width=40)
    feedback_entry.pack(pady=10)

    def submit_feedback():
        feedback_message = feedback_entry.get("1.0", "end-1c").strip()

        if not feedback_message:
            messagebox.showerror("Error", "Feedback message cannot be empty.")
            return

        try:
            conn = create_connection()
            cursor = conn.cursor()

            cursor.execute("""INSERT INTO feedback (userId, message) VALUES (%s, %s)""", (user_id, feedback_message))
            conn.commit()

            messagebox.showinfo("Success", "Feedback submitted successfully.")
            form.destroy()

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Database Error", str(err))

        finally:
            cursor.close()
            conn.close()

    tk.Button(form, text="Submit Feedback", command=submit_feedback, bg="#4CAF50", fg="white").pack(pady=20)

def open_feedback_status_window(user_id):
    form = tk.Toplevel()
    form.title("Feedback Status")
    form.geometry("400x400")

    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""SELECT message, adminReply FROM feedback WHERE userId = %s""", (user_id,))
        feedback_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if feedback_data:
            tk.Label(form, text=f"Your Feedback: {feedback_data['message']}", font=("Arial", 12)).pack(pady=10)
            tk.Label(form, text=f"Admin's Reply: {feedback_data['adminReply'] or 'No reply yet.'}", font=("Arial", 12)).pack(pady=10)
        else:
            messagebox.showinfo("No Feedback", "You haven't submitted any feedback yet.")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

def open_feedback_management_window(admin_id):
    form = tk.Toplevel()
    form.title("Manage Feedback")
    form.geometry("400x400")

    tk.Label(form, text="Manage Feedback and Replies:").pack(pady=10)

    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""SELECT feedbackId, message FROM feedback""")
        feedbacks = cursor.fetchall()

        for feedback in feedbacks:
            feedback_frame = tk.Frame(form)
            feedback_frame.pack(pady=5)

            tk.Label(feedback_frame, text=f"Feedback: {feedback['message']}", font=("Arial", 12)).pack(pady=5)
            tk.Label(feedback_frame, text="Reply:").pack(pady=5)

            reply_entry = tk.Entry(feedback_frame, width=40)
            reply_entry.pack(pady=5)

            def submit_reply(feedback_id, reply):
                try:
                    conn = create_connection()
                    cursor = conn.cursor()

                    cursor.execute("""UPDATE feedback SET adminReply = %s WHERE feedbackId = %s""", (reply, feedback_id))
                    conn.commit()

                    messagebox.showinfo("Success", "Reply submitted successfully.")
                except mysql.connector.Error as err:
                    conn.rollback()
                    messagebox.showerror("Database Error", str(err))

            tk.Button(feedback_frame, text="Submit Reply", command=lambda: submit_reply(feedback['feedbackId'], reply_entry.get())).pack(pady=5)

        conn.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
