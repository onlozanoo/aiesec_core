# etl/extract_lcs.py

import logging
import pandas as pd
import os
import sys

# --- Relative Imports within the ETL package ---
# Assumes config, utils, scraper, processing are in the same 'etl' directory
try:
    from .config import (
        COUNTRY_CODES_CSV_PATH,
        COUNTRY_ID_COLUMN,
        COUNTRY_NAME_COLUMN
    )
    from .utils import get_country_codes_dict_from_csv
    from .scraper import AIESECScraper
    from .processing import process_data # Use the main processing function
except ImportError as e:
    # This might happen if the script is run directly, handle appropriately
    logging.error(f"Error importing sibling modules: {e}. Ensure running via main script or tests setup.")
    # Fallback or re-raise depending on desired behavior when run directly
    # For now, let's assume it's run via update_data.py which sets up paths correctly if needed
    # Alternatively, adjust sys.path here if direct execution is needed, but it's less clean.
    # Adding project root to path if run directly (less ideal)
    # project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # if project_root not in sys.path:
    #    sys.path.insert(0, project_root)
    #    from etl.config import ... # try again with absolute path from root
    raise # Re-raise the error if imports fail, indicating a setup problem

# Configure logging (optional, can be handled by the calling script)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

def extract_all_data() -> pd.DataFrame:
    """
    Runs the entire ETL process: Load codes, scrape data, process data.

    Returns:
        A pandas DataFrame containing the final, processed data,
        or an empty DataFrame if the process fails.
    """
    logging.info("--- Starting AIESEC LC Data Extraction Process ---")
    final_df = pd.DataFrame() # Initialize empty DataFrame

    # 1. Load Country Codes
    logging.info(f"Loading country codes from: {COUNTRY_CODES_CSV_PATH}")
    country_codes, country_region_dict = get_country_codes_dict_from_csv(
        COUNTRY_CODES_CSV_PATH,
        id_col=COUNTRY_ID_COLUMN,
        name_col=COUNTRY_NAME_COLUMN
    )

    if not country_codes:
        logging.error("Failed to load country codes. ETL process cannot continue.")
        return final_df # Return empty DataFrame

    # 2. Initialize and Run Scraper
    scraper = AIESECScraper()
    raw_data_df = pd.DataFrame() # Initialize empty df for raw data

    try:
        logging.info("Starting the scraping sub-process...")
        raw_data_df = scraper.run_scraper(country_codes, country_region_dict)
        logging.info(f"Scraping finished. Received raw DataFrame with {len(raw_data_df)} rows.")

    except Exception as e:
        logging.error(f"An critical error occurred during scraping: {e}", exc_info=True)
        # Depending on requirements, might return here or try processing partial data
    finally:
        # Always close the session
        scraper.close_session()

    # 3. Process/Clean Data
    if not raw_data_df.empty:
        logging.info("Starting data processing step...")
        try:
            final_df = process_data(raw_data_df) # Call main processing function
            logging.info(f"Data processing finished. Final DataFrame has {len(final_df)} rows.")
        except Exception as e:
            logging.error(f"An error occurred during data processing: {e}", exc_info=True)
            logging.warning("Returning raw data due to processing error.")
            final_df = raw_data_df # Fallback to raw data if processing fails
    else:
        logging.warning("Raw data DataFrame from scraper is empty. Skipping processing.")
        final_df = raw_data_df # Keep it as empty DF

    logging.info("--- AIESEC LC Data Extraction Process Finished ---")
    return final_df

# Example of how to call if run directly (for testing)
if __name__ == '__main__':
    # Need to handle path for direct execution if necessary
    # Or configure logging here if not done by caller
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    print("Running ETL process directly...")
    extracted_df = extract_all_data()
    print(f"ETL process completed. DataFrame shape: {extracted_df.shape}")
    if not extracted_df.empty:
        print("DataFrame Head:")
        print(extracted_df.head()) 