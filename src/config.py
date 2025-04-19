import os
import logging

# --- Project Root ---
# Assumes config.py is in src/, and src/ is one level down from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Scraping Configuration ---
BASE_URL = "https://core.aiesec.org.eg/analytics/"
DEFAULT_VIEW_SUFFIX = "LC25/" # The specific view/LC ID suffix
REQUEST_DELAY_SECONDS = 1 # Delay between requests to be polite
DEFAULT_USER_AGENT = 'MyAIESECDataScraper/1.0 (Contact: your_email@example.com)' # Replace with actual contact if desired
HEADERS = {
    'User-Agent': DEFAULT_USER_AGENT
    # Add other headers if necessary
}

# --- File Paths ---
# Construct paths relative to the project root
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

COUNTRY_CODES_CSV_FILENAME = 'codigos.csv' # Name of the input CSV file
OUTPUT_CSV_FILENAME = 'aiesec_lc_data_output.csv' # Name of the output CSV file
OUTPUT_CSV_FILENAME_CONVERSION_RATES = 'aiesec_lc_data_output_conversion_rates.csv' # Name of the output CSV file
LOG_FILENAME = 'scraper.log' # Name of the log file

COUNTRY_CODES_CSV_PATH = os.path.join(DATA_DIR, COUNTRY_CODES_CSV_FILENAME)
OUTPUT_CSV_PATH = os.path.join(DATA_DIR, OUTPUT_CSV_FILENAME)
OUTPUT_CSV_PATH_CONVERSION_RATES = os.path.join(DATA_DIR, OUTPUT_CSV_FILENAME_CONVERSION_RATES)
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILENAME)

# --- Input CSV Configuration ---
# Column names expected in the COUNTRY_CODES_CSV_PATH file
COUNTRY_ID_COLUMN = 'Country_ID'
COUNTRY_NAME_COLUMN = 'Country_Name'

# --- Logging Configuration ---
LOG_LEVEL = logging.INFO # Default logging level (e.g., INFO, DEBUG)
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(module)s - %(message)s'

# --- Data Processing Configuration (Optional - Add as needed) ---
# Example: Define expected columns after parsing, default values, etc.
# EXPECTED_COLUMNS = ['Country_ID', 'Country_Name', 'LC_Name', ...]
# DEFAULT_NUMERIC_VALUE = 0

# --- Output Configuration ---
OUTPUT_SEPARATOR = ';' # Separator for the output CSV file
OUTPUT_ENCODING = 'utf-8' # Encoding for the output CSV file
