import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os
from datetime import datetime
from extract import extract_invoice_data
from validate import validate_invoice
from database import save_invoice,search_by_invoice,search_by_vendor, filter_by_date,filter_by_payment_status,filter_by_invoice_amount,update_payment_status,delete_invoice,get_all_invoices_df
from reports import daily_invoice_report,monthly_invoice_summary,vendor_report,tax_summary,outstanding_payments
from export import export_csv,export_excel,export_pdf
from logs import log_file_upload,log_processing_success,log_validation_errors,log_export,log_processing_failure

st.set_page_config(page_title="Invoice Processing System",page_icon="icon.png",layout="wide")

# SESSION STATE
if "processed_invoices" not in st.session_state:
    st.session_state.processed_invoices = []

left,center,right = st.columns(3)
with center:
    st.image('icon.png', width=80)
# SIDEBAR
st.sidebar.image('icon.png',width=50)
st.sidebar.title("Invoice Management")

page = st.sidebar.radio("Navigation",["Dashboard","Upload Invoice","Database","Reports","Export","Activity Logs"])

# ----------DASHBOARD-------------
if page == "Dashboard":
    st.title("Dashboard")
    st.caption("Invoice Processing & Management System")
    try:
        df = get_all_invoices_df()
    except Exception as e:
        st.error(f"Error occured: {e}")
        df = pd.DataFrame()

    total_invoices = len(df)

    if not df.empty and "payment_status" in df.columns:
        total_paid = int(
            (df["payment_status"] == "Paid").sum()
        )
    else:
        total_paid = 0

    if not df.empty and "payment_status" in df.columns:
        total_unpaid = int((df["payment_status"] == "Unpaid").sum())
        
    else:
        total_unpaid = 0
    
    if not df.empty and "total_amount" in df.columns:
        total_revenue = pd.to_numeric(df["total_amount"]).sum()
        
    else:
        total_revenue = 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoices",total_invoices)
    c2.metric("Paid",total_paid)
    c3.metric("Unpaid",total_unpaid)
    c4.metric("Revenue",f"{total_revenue:,.2f}")

    st.divider()

    if not df.empty:
        if "payment_status" in df.columns:
            status_counts = (df["payment_status"].value_counts())
        col1,col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.pie(status_counts,labels=status_counts.index,autopct="%1.1f%%",wedgeprops={"width": 0.4})
            ax.set_title("Payment Status Distribution")
            st.pyplot(fig)

        with col2:
            if "invoice_date" in df.columns and "total_amount" in df.columns:
                monthly_data = (df.groupby(df["invoice_date"].str[:8])["total_amount"].sum())
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(monthly_data.index,monthly_data.values, marker="o",linewidth=2)
            ax.set_title("Monthly Revenue")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Amount")
            ax.tick_params(axis="x", rotation=45)
            st.pyplot(fig)
# --------------UPLOAD INVOICE------------
elif page == "Upload Invoice":
    st.title("Upload Invoice")
    files = st.file_uploader("Upload Invoice PDFs",type=["pdf"],accept_multiple_files=True)

    if files:
        for file in files:
            log_file_upload(file.name)
            try:
                with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
                    tmp.write(file.read())
                    temp_path = tmp.name
                with st.spinner(f"Processing {file.name}..."):
                    invoice = extract_invoice_data(temp_path)
                    errors = validate_invoice(invoice)
                    st.subheader(file.name)
                    st.json(invoice)
                    if errors:
                        st.error("Validation Failed")
                        st.write(invoice['Invoice Date'])
                        for error in errors:
                            st.write("•", error)
                        log_validation_errors(invoice.get("Invoice Number","Unknown"),errors)

                    else:
                        invoice["Processing Date"] = (datetime.now().strftime("%Y-%m-%d"))
                        invoice["Validation Status"] = ("Valid" if not errors else "Invalid")
                        save_invoice(invoice)
                        log_processing_success(invoice.get("Invoice Number","Unknown"))
                        st.success("Invoice saved successfully.")
                os.remove(temp_path)

            except Exception as e:
                st.error(str(e))
                log_processing_failure(file.name,e)

# ---------DATABASE MANAGEMENT----------
elif page == "Database":
    st.title("Database Management")
    tab1, tab2, tab3 = st.tabs(["Search","Update","Delete"])

    with tab1:
        option = st.selectbox("Search By",["Invoice Number","Vendor","Date","Payment Status","Invoice Amount"])
        if option == "Invoice Number":
            inv = st.text_input("Invoice Number",key="search")
            if st.button("Search"):
                rows = search_by_invoice(inv)
                if rows:
                    st.dataframe(pd.DataFrame(rows))
                else:
                    st.info("No records found.")

        elif option == "Vendor":
            vendor = st.text_input("Vendor Name")
            if st.button("Search Vendor"):
                rows = search_by_vendor(vendor)

                if rows:
                    st.dataframe(pd.DataFrame(rows))
                else:
                    st.info("No records found.")

        elif option == "Date":
            d = st.date_input("Invoice Date")
            if st.button("Filter Date"):
                rows = filter_by_date(str(d))
                st.dataframe(pd.DataFrame(rows))

        elif option == "Payment Status":
            status = st.selectbox("Status",["Paid","Unpaid"])

            if st.button("Filter Status"):
                rows = (filter_by_payment_status(status))
                st.dataframe(pd.DataFrame(rows))
        elif option == "Invoice Amount":
            amount = st.text_input("Invoice Amount")
            if st.button("Search Amount"):
                rows = filter_by_invoice_amount(amount)
                if rows:
                    st.dataframe(pd.DataFrame(rows))
                else:
                    st.info("No records found.")

    with tab2:
        st.subheader("Update Payment Status")
        invoice_no = st.text_input("Invoice Number")
        status = st.selectbox("Payment Status",["Paid","Unpaid"])
        if st.button("Update Status"):
            update_payment_status(invoice_no,status)
            st.success("Invoice updated.")

    with tab3:
        st.subheader("Delete Invoice")
        invoice_no = st.text_input("Invoice Number to Delete")
        confirm = st.checkbox("I understand this action cannot be undone.")

        if confirm:
            if st.button("Delete"):
                delete_invoice(invoice_no)
                st.success("Invoice deleted successfully.")

# -----------REPORTS-------------
elif page == "Reports":
    st.title("Reports")
    report_type = st.selectbox("Select Report",["Daily Report","Monthly Summary","Vendor Report","Tax Summary","Outstanding Payments"])
    if report_type == "Daily Report":
        d = st.date_input("Date")
        if st.button("Generate Daily Report"):
            df = daily_invoice_report(str(d))
            st.dataframe(df)

    elif report_type == "Monthly Summary":
        month = st.text_input("Month (YYYY-MM)")
        if st.button("Generate Summary"):
            summary = (monthly_invoice_summary(month))
            st.json(summary)

    elif report_type == "Vendor Report":
        if st.button("Generate Vendor Report"):
            df = vendor_report()
            st.dataframe(df)

    elif report_type == "Tax Summary":
        if st.button("Generate Tax Summary"):
            st.dataframe(tax_summary())

    elif report_type == "Outstanding Payments":
        if st.button("Generate Report"):
            st.dataframe(outstanding_payments())

# -----------EXPORT---------------
elif page == "Export":
    st.title("Export Data")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Export CSV"):
            export_csv()
            log_export("invoices.csv")
            st.success("CSV exported.")

    with c2:
        if st.button("Export Excel"):
            export_excel()
            log_export("invoices.xlsx")
            st.success("Excel exported.")

    with c3:
        if st.button("Export PDF"):
            export_pdf()
            log_export("invoice_report.pdf")
            st.success("PDF exported.")

# ----------ACTIVITY LOGS-----------
elif page == "Activity Logs":
    st.title("Activity Logs")
    try:
        with open("invoice_system.log","r",encoding="utf-8") as f:
            logs = f.read()
        st.text_area("Logs",logs,height=500)

    except FileNotFoundError:
        st.info("No logs available yet.")

st.divider()
