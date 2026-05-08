import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, 'database.db')
SCHEMA_FILE = os.path.join(BASE_DIR, 'schema.sql')

def run_schema():
    if not os.path.exists(SCHEMA_FILE):
        print("schema.sql not found.")
        return
    if os.path.exists(DB_FILE):
        print("database.db already exists. If you want a fresh DB, delete database.db first.")
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()
    print("Schema executed, database.db created.")
    seed_initial(conn)
    conn.close()

def seed_initial(conn):
    cursor = conn.cursor()
    # Use default secure hashing (Werkzeug default) or explicit pbkdf2:sha256
    admin_pass = generate_password_hash('admin123')  # secure default
    sales_pass = generate_password_hash('sales123')
    cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", ('admin', admin_pass, 'Admin'))
    cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", ('sales', sales_pass, 'Sales'))

    products = [
        ('Product A', 'Category 1', 10.0, 50),
        ('Product B', 'Category 2', 25.0, 20),
        ('Product C', 'Category 1', 7.5, 8)
    ]
    cursor.executemany("INSERT INTO product (name, category, price, quantity) VALUES (?, ?, ?, ?)", products)
    conn.commit()
    print("Seed data inserted: users (admin/sales) and sample products.")

if __name__ == '__main__':
    run_schema()
