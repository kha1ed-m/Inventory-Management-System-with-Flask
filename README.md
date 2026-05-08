Mini ERP - Inventory & Sales Management System
A robust, lightweight Inventory Management System built with Flask and SQLAlchemy. This application features role-based access control, real-time stock tracking, and automated sales reporting.

🚀 Features
🔐 Authentication & Roles
Role-Based Access Control (RBAC): Distinct interfaces and permissions for Admin and Sales users.

Secure Authentication: Password hashing using Werkzeug for user security.

📦 Admin Capabilities
Inventory Management: Add, view, and delete products with real-time stock updates.

Smart Reporting: Dashboard for total sales, order counts, and automated Low Stock Alerts (for items < 5 units).

Data Pagination: Efficient browsing of large product and order lists.

💰 Sales Capabilities
Order Creation: Streamlined interface for placing orders with automatic stock deduction.

Order History: Detailed view of past orders including unit prices and timestamps.

🛠️ Tech Stack
Backend: Python / Flask

Database: SQLite / SQLAlchemy ORM

Frontend: Jinja2 Templates, HTML5, CSS3

Testing: Pytest

⚙️ Installation & Setup
1-Clone the repository:

Bash
git clone https://github.com/kha1ed-m/Inventory-Management-System-with-Flask.git
cd Inventory-Management-System-with-Flask

3-Set up Virtual Environment:

Bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

4-Install Dependencies:

Bash
pip install -r requirements.txt
Initialize the Database:
Run the initialization script to create the schema and seed initial data (Admin/Sales users).

Bash
python int_db.py
Run the Application:

Bash
python app.py
Access the app at http://127.0.0.1:5000

🔑 Default Credentials
Admin: admin / admin123

Sales: sales / sales123# Inventory-Management-System-with-Flask
