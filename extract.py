import re
import pymupdf


def extract_invoice_data(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()

    invoice = {
        "Invoice Number": None,
        "Vendor Name": None,
        "Customer Name": None,
        "Invoice Date": None,
        "Due Date": None,
        "Tax Amount": None,
        "Total Amount": None,
        "Currency": None,
        "Payment Status": "Unpaid"
    }

    # Normalize text
    text = text.replace("\r", "")
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    patterns = {
        "Invoice Number": [r"Invoice\s*(?:Number|No\.?|#)\s*:\s*([^\n]+)"],
        "Vendor Name": [r"Vendor\s*(?:Name)?\s*:\s*([^\n]+)"],
        "Customer Name": [r"Customer\s*(?:Name)?\s*:\s*([^\n]+)"],
        "Invoice Date": [r"Invoice\s*Date\s*:\s*([^\n]+)"],
        "Due Date": [r"Due\s*Date\s*:\s*([^\n]+)"],
        "Tax Amount": [r"Tax\s*(?:Amount)?\s*:\s*([^\n]+)"],
        "Total Amount": [r"Total\s*Amount\s*:\s*([^\n]+)",r"Invoice\s*Total\s*:\s*([^\n]+)",r"Total\s*:\s*([^\n]+)"],
        "Currency": [r"Currency\s*:\s*([^\n]+)"],
        "Payment Status": [r"Payment\s*Status\s*:\s*([^\n]+)"]
    }

    for field, regex_list in patterns.items():
        for pattern in regex_list:
            match = re.search(pattern,text,re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                value = value.replace("Rs.", "")
                value = value.replace("PKR", "PKR")
                value = value.replace("$", "")
                invoice[field] = value.strip()
                break

    # Extract Currency Automatically
    if not invoice["Currency"]:
        if re.search(r"\bPKR\b", text, re.IGNORECASE):
            invoice["Currency"] = "PKR"
        elif re.search(r"\bUSD\b", text, re.IGNORECASE):
            invoice["Currency"] = "USD"
        elif re.search(r"\bEUR\b", text, re.IGNORECASE):
            invoice["Currency"] = "EUR"

    # Extract Payment Status Automatically
    if not invoice["Payment Status"]:
        if re.search(r"\bPaid\b", text, re.IGNORECASE):
            invoice["Payment Status"] = "Paid"

        else:
            invoice["Payment Status"] = "Unpaid"
    print(invoice)

    return invoice