# update_data.py

import os
import sys
import pandas as pd
import logging
from datetime import datetime

# --- Add etl directory to path if needed (e.g., running from root) ---
# This ensures the 'etl' package can be found
project_root = os.path.dirname(os.path.abspath(__file__))
etl_path = os.path.join(project_root, 'etl')
if etl_path not in sys.path:
    sys.path.insert(0, etl_path)

# --- Import the main ETL function ---
try:
    from etl.extract_lcs import extract_all_data
    # Import config for paths if needed, or define paths here
    from etl.config import DATA_DIR, LOG_DIR, LOG_FILE_PATH, LOG_LEVEL, LOG_FORMAT
except ImportError as e:
    print(f"Error importing ETL module: {e}")
    print("Ensure the 'etl' directory exists and contains the necessary modules (__init__.py, extract_lcs.py, etc.).")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

# --- Setup Logging ---
# Configure logging here, so it's active for the whole process
log_formatter = logging.Formatter(LOG_FORMAT)
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
# Avoid adding handlers multiple times if script is re-run in same session
if not root_logger.hasHandlers():
    root_logger.addHandler(console_handler)

    # Optional: File handler
    try:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8')
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
        logging.info(f"Logging to console and file: {LOG_FILE_PATH}")
    except Exception as e:
        logging.error(f"Failed to set up file logging to {LOG_FILE_PATH}: {e}")
        logging.info("Logging to console only.")
else:
     logging.info("Logger already configured.")

# --- Main Execution Logic ---
if __name__ == "__main__":
    logging.info("=== Starting Data Update Process ===")

    # 1. Execute the ETL process and get the final DataFrame
    logging.info("Running the main ETL function: extract_all_data()...")
    try:
        final_df = extract_all_data()
    except Exception as e:
        logging.error(f"ETL process failed with an error: {e}", exc_info=True)
        final_df = pd.DataFrame() # Ensure df is empty on failure

    # Check if the ETL process returned a valid DataFrame
    if isinstance(final_df, pd.DataFrame) and not final_df.empty:
        logging.info(f"ETL process successful. Received {len(final_df)} rows.")

        # 2. Define output paths within the DATA_DIR
        current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_filename = f"data_{current_timestamp}.csv"
        latest_filename = "data_latest.csv"
        output_path_timestamped = os.path.join(DATA_DIR, timestamped_filename)
        output_path_latest = os.path.join(DATA_DIR, latest_filename)

        # Ensure data directory exists
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            logging.info(f"Created data directory: {DATA_DIR}")

        # 3. Save timestamped Parquet file
        try:
            logging.info(f"Saving timestamped data to: {output_path_timestamped}")
            # You might need to install pyarrow: pip install pyarrow
            final_df.to_csv(output_path_timestamped, index=False, sep=';')
            logging.info("Timestamped file saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save timestamped parquet file: {e}", exc_info=True)

        # 4. (Optional) Save/Update the 'latest' file alias
        try:
            logging.info(f"Updating latest data alias: {output_path_latest}")
            final_df.to_csv(output_path_latest, index=False, sep=';')
            logging.info("Latest file alias updated successfully.")
        except Exception as e:
            logging.error(f"Failed to save/update latest parquet file: {e}", exc_info=True)

    elif isinstance(final_df, pd.DataFrame) and final_df.empty:
         logging.warning("ETL process completed but returned an empty DataFrame. No file saved.")
    else:
         logging.error("ETL process did not return a valid DataFrame. No file saved.")


    # 5. (Optional) Open Power BI automatically
    open_pbix_flag = True # Set to False to disable
    pbix_relative_path = "dashboard/dashboard_principal.pbix" # Relative path from project root
    pbix_absolute_path = os.path.abspath(os.path.join(project_root, pbix_relative_path))

    if open_pbix_flag:
        if os.path.exists(pbix_absolute_path):
            logging.info(f"Attempting to open Power BI dashboard: {pbix_absolute_path}")
            try:
                # Use os.startfile on Windows, or 'open' on macOS, 'xdg-open' on Linux
                if sys.platform == "win32":
                    os.startfile(pbix_absolute_path)
                elif sys.platform == "darwin": # macOS
                    os.system(f'open "{pbix_absolute_path}"')
                else: # Linux and other POSIX
                    os.system(f'xdg-open "{pbix_absolute_path}"')
                logging.info("Command to open Power BI sent.")
            except Exception as e:
                logging.error(f"Failed to automatically open Power BI: {e}", exc_info=True)
                logging.error("Please open the dashboard manually.")
        else:
            logging.warning(f"Power BI file not found at expected location: {pbix_absolute_path}. Cannot open automatically.")
    else:
        logging.info("Skipping automatic Power BI opening.")

    logging.info("=== Data Update Process Finished ===") 