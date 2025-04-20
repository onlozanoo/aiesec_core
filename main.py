import os
import sys
import pandas as pd
import logging


# --- Add 'src' directory to PYTHONPATH ---
# This allows importing modules from 'src' when running main.py from the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# --- End of path configuration ---

# --- Now we can import from modules within src ---
try:
    from utils import get_country_codes_dict_from_csv #, save_data (Implement save_data later)
    from scraper import AIESECScraper
    from processing import process_data
    from config import (
        COUNTRY_CODES_CSV_PATH,
        OUTPUT_CSV_PATH,
        LOG_LEVEL,
        LOG_FILE_PATH,
        LOG_DIR,
        LOG_FORMAT,
        COUNTRY_ID_COLUMN,
        COUNTRY_NAME_COLUMN,
        COUNTRY_REGION_COLUMN,
        OUTPUT_SEPARATOR,
        OUTPUT_ENCODING
    )
except ImportError as e:
    print(f"Error importing modules from src: {e}")
    print("Ensure you are running main.py from the project root directory 'aiesec_scraper/'")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1) # Exit if imports fail

# --- Configuration (Replace with imports from config.py later) ---
# Construct paths relative to the project root (where main.py is)
# Optional: Configure logging to file
LOG_FILE = os.path.join(LOG_DIR, 'scraper.log')

# --- Setup Logging ---
def setup_logging():
    """Configures logging."""
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # Optional: File handler
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8') # Append mode
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        logging.info(f"Logging to console and file: {LOG_FILE}")
    except Exception as e:
        logging.error(f"Failed to set up file logging to {LOG_FILE}: {e}")  
        logging.info("Logging to console only.")

# --- Main Execution Function ---
def run_main_scraper(codes_csv_path: str, output_csv_path: str):
    """Main function to run the scraper workflow."""
    logging.info("--- Starting Main Scraper Execution ---")

    # 1. Load Country Codes
    logging.info(f"Loading country codes from: {codes_csv_path}")
    # Make sure column names match your CSV and the function's defaults/parameters
    country_codes, region_map = get_country_codes_dict_from_csv(codes_csv_path, id_col='Country_ID', name_col='Country_Name', region_col='Country_Region')

    if not country_codes:
        logging.error("Failed to load country codes. Exiting.")
        return

    # 2. Initialize and Run Scraper
    scraper = AIESECScraper()
    raw_data_df = pd.DataFrame() # Initialize empty df

    try:
        logging.info("Starting the scraping process...")
        # run_scraper now returns a DataFrame
        raw_data_df = scraper.run_scraper(country_codes, region_map)
        logging.info(f"Scraping finished. Received DataFrame with {len(raw_data_df)} rows.")

    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}", exc_info=True)
    finally:
        # Always close the session
        scraper.close_session()

    # 3. Process/Clean Data (Placeholder - Requires processing.py)
    if not raw_data_df.empty:
        logging.info("Proceeding to data cleaning/processing step")
        try:
            cleaned_df = process_data(raw_data_df) # Call cleaning function when implemented
            logging.info("Data cleaning/processing finished.")
        except Exception as e:
            logging.error(f"An error occurred during data processing: {e}", exc_info=True)
            cleaned_df = raw_data_df # Fallback to raw data if cleaning fails
            logging.warning("Using raw data due to processing error.")
    else:
        logging.warning("Raw data DataFrame is empty. Skipping processing and saving.")
        cleaned_df = raw_data_df # Keep it as empty DF

    # 4. Save Data (Placeholder - Requires save_data in utils or similar)
    if not cleaned_df.empty:
        logging.info(f"Saving final DataFrame to: {output_csv_path}")
        try:
            # --- Implement saving logic ---
            # Example using pandas directly:
            output_dir = os.path.dirname(output_csv_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # Save the entire result at the end. Consider chunking for very large files.
            cleaned_df.to_csv(output_csv_path, index=False, encoding='utf-8', sep=';') # Using semicolon separator
            logging.info(f"Successfully saved data to {output_csv_path}")
            # Or call a function like: save_data(cleaned_df, output_csv_path)
        except Exception as e:
            logging.error(f"Failed to save data to {output_csv_path}: {e}", exc_info=True)
    else:
        logging.info("Final DataFrame is empty. No data saved.")


    logging.info("--- Main Scraper Execution Finished ---")


# --- Script Entry Point ---
if __name__ == "__main__":
    setup_logging()
    # You could use argparse here to accept paths from command line arguments
    codes_file = COUNTRY_CODES_CSV_PATH
    output_file = OUTPUT_CSV_PATH
    run_main_scraper(codes_file, output_file)
