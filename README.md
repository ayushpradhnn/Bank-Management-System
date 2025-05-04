This is a Bank Management System built using Python (Tkinter) and MySQL.
It manages customer accounts, transactions, loans, and feedback through separate Admin and Customer interfaces.

✨ Features
🔒 Secure Login System
Separate login for Admins and Customers.

Credentials are securely stored in the database.

🏦 Banking Operations (for Customers)
Deposit money into accounts.

Withdraw funds from accounts.

Transfer money between accounts.

View Transaction History of all activities.

💸 Loan Management
Customers can apply for loans.

Admins can view, approve, or reject loan applications.

Admins can set interest rates.

Customers can track loan status and view assigned interest rates.

💬 Feedback System
Customers can submit feedback.

Admins can reply to customer feedback.

🗄️ Database Structure
Fully normalized MySQL database with tables for:

Users

Bank Accounts

Transactions

Loans

Cards

Feedback

🚀 Technologies Used
Frontend: Python (Tkinter GUI)

Backend: MySQL Database

Connector: mysql-connector-python

Language: Python 3

⚙️ Setup Instructions
Clone the repository:

bash

Install dependencies:

bash
Copy
Edit
pip install mysql-connector-python
Setup the MySQL database:

Create a new database in MySQL.

Import the provided .sql file or manually create the required tables according to the ER diagram.

Update the database connection settings (host, user, password, database) in your Python files if needed.

Run the application:

bash
Copy
Edit
python main.py
🔑 Important Notes
Admin accounts must be created manually through MySQL.
To access the admin panel, insert an admin entry directly into the login table with appropriate email, password, and role as 'admin'.

Customers can register via the admin panel and complete their profile after logging in
