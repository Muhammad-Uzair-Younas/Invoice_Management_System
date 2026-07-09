import pandas as pd
import sqlite3
import pymupdf

conn = sqlite3.connect("invoices.db",check_same_thread=False)

def get_all_invoices():
    query = "SELECT * FROM invoices"
    return pd.read_sql_query(query, conn)

def export_csv():
    filename="invoices_report.csv"
    df = get_all_invoices()
    df.to_csv(filename, index=False)


def export_excel():
    filename="invoices_report.xlsx"
    df = get_all_invoices()
    df.to_excel(filename, index=False)

def export_pdf(filename="invoices_report.pdf"):
    df = get_all_invoices()
    doc = pymupdf.open()
    page = doc.new_page()
    y = 50

    page.insert_text((50, y),"Invoice Summary Report",fontsize=16)
    y += 40

    for _, row in df.iterrows():
        line = (
            f"Invoice: {row['invoice_number']} | "
            f"Vendor: {row['vendor_name']} | "
            f"Amount: {row['total_amount']} | "
            f"Status: {row['payment_status']}"
        )

        page.insert_text((50, y),line,fontsize=11)

        y += 20
        if y > 750:
            page = doc.new_page()
            y = 50
    doc.save(filename)
    doc.close()