from datetime import datetime
import re
invoice_numbers = set()
def validate_invoice(invoice):
    errors = []

    # 1. Missing fields
    for key, value in invoice.items():
        if value is None or str(value).strip() == "":
            errors.append(f"{key} is missing.")

    # 2. Duplicate invoice number
    invoice_no = invoice.get("Invoice Number")
    if invoice_no:
        if invoice_no in invoice_numbers:
            errors.append("Duplicate Invoice Number.")
        else:
            invoice_numbers.add(invoice_no)

    # 3. Date format validation
    for field in ["Invoice Date", "Due Date"]:
        date = invoice.get(field)
        if date:
            date = date.strip()
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                errors.append(f"{field} must be YYYY-MM-DD.")

    # 4. Numeric validation
    for field in ["Tax Amount", "Total Amount"]:
        value = invoice.get(field)
        if value:
        # Remove commas, currency symbols, spaces, etc.
            clean_value = re.sub(r"[^\d.]", "", value)
            try:
                float(clean_value)
            except ValueError:
                errors.append(f"{field} must be numeric.")
    return errors