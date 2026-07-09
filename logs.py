import logging
from pathlib import Path

LOG_FILE = "invoice_system.log"

logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


# 1. Uploaded Files
def log_file_upload(file):
    file = Path(file)
    logger.info(f"Uploaded file: {file.name}")

# 2. Processing History
def log_processing_success(invoice_number):
    logger.info(f"Invoice {invoice_number} processed successfully.")

# 3. Validation Errors
def log_validation_errors(invoice_number, errors):
    for error in errors:
        logger.error(f"Invoice {invoice_number}: {error}")

# 4. Export History
def log_export(filename):
    logger.info(f"Data exported to {filename}")

# 5. Failed Processing Attempts
def log_processing_failure(file, error):
    file = Path(file)
    logger.error(f"Failed to process {file.name}: {error}")