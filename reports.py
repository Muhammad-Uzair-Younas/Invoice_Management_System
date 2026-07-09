import sqlite3
import pandas as pd

conn = sqlite3.connect("invoices.db",check_same_thread=False)

def daily_invoice_report(date):
    query = """
    SELECT * FROM invoices
    WHERE TRIM(invoice_date) = ?"""
    df = pd.read_sql_query(query, conn, params=(date,))
    return df

def monthly_invoice_summary(month):
    query = """
    SELECT * FROM invoices
    WHERE substr(TRIM(invoice_date),1,7)=?"""
    df = pd.read_sql_query(query, conn, params=(month,))
    summary = {
        "Total Invoices": len(df),
        "Total Amount": df["total_amount"].sum(),
        "Total Tax": df["tax_amount"].sum()
    }
    return summary

def vendor_report():
    query = """
    SELECT vendor_name,
    COUNT(*) AS total_invoices,
    SUM(total_amount) AS total_amount FROM invoices
    GROUP BY vendor_name"""
    return pd.read_sql_query(query, conn)


def tax_summary():
    query = """
    SELECT
    SUM(tax_amount) AS total_tax
    FROM invoices
    """
    return pd.read_sql_query(query, conn)


def outstanding_payments():
    query = """
    SELECT *
    FROM invoices
    WHERE payment_status = 'Unpaid'"""
    return pd.read_sql_query(query, conn)


