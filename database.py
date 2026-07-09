import sqlite3
import pandas as pd
conn = sqlite3.connect("invoices.db",check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE,
    vendor_name TEXT,
    customer_name TEXT,
    invoice_date TEXT,
    due_date TEXT,
    tax_amount REAL,
    total_amount REAL,
    currency TEXT,
    payment_status TEXT,
    processing_date TEXT,
    validation_status TEXT
)
""")

conn.commit()

def save_invoice(invoice):
    cursor.execute("""
    INSERT INTO invoices (
        invoice_number,
        vendor_name,
        customer_name,
        invoice_date,
        due_date,
        tax_amount,
        total_amount,
        currency,
        payment_status,
        processing_date,
        validation_status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    (
        invoice["Invoice Number"],
        invoice["Vendor Name"],
        invoice["Customer Name"],
        invoice["Invoice Date"],
        invoice["Due Date"],
        invoice["Tax Amount"],
        invoice["Total Amount"],
        invoice["Currency"],
        invoice["Payment Status"],
        invoice["Processing Date"],
        invoice["Validation Status"]
    ))

    conn.commit()

def get_all_invoices_df():
    return pd.read_sql_query("SELECT * FROM invoices",conn)

def search_by_invoice(invoice_number):
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?",(invoice_number,))
    return cursor.fetchall()

def search_by_vendor(vendor):
    cursor.execute("SELECT * FROM invoices WHERE vendor_name LIKE ?",(f"%{vendor}%",))
    return cursor.fetchall()

def filter_by_date(date):
    cursor.execute("SELECT * FROM invoices WHERE TRIM(invoice_date) = ?",(date,))
    return cursor.fetchall()


def filter_by_payment_status(status):
    cursor.execute("SELECT * FROM invoices WHERE payment_status = ?",(status,))
    return cursor.fetchall()

def filter_by_invoice_amount(amount):
    cursor.execute("SELECT * FROM invoices WHERE total_amount = ?",(amount,))
    return cursor.fetchall()

def update_payment_status(invoice_number, status):
    cursor.execute("""
        UPDATE invoices
        SET payment_status = ? WHERE invoice_number = ?""",(status, invoice_number))
    conn.commit()


def delete_invoice(invoice_number):
    cursor.execute("DELETE FROM invoices WHERE invoice_number = ?",(invoice_number,))
    conn.commit()

