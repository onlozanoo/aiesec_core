import pandas as pd
import logging
import os
from typing import Dict, Optional # For type hints
# Use a relative import here so this module works whether the package is loaded
# via its package name or executed directly. Importing "config" absolutely can
# fail when the caller does not manipulate ``sys.path`` in the same way as the
# development environment.
# Prefer a relative import when used as part of the package but provide a
# fallback to support running this module directly.
try:
    from .config import COUNTRY_ID_COLUMN, COUNTRY_NAME_COLUMN
except ImportError:  # pragma: no cover - direct execution fallback
    from config import COUNTRY_ID_COLUMN, COUNTRY_NAME_COLUMN

# Basic logging configuration (can be moved to config.py or main.py for centralization)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_country_codes_dict_from_csv(
    filepath: str,
    id_col: str = 'Country_ID',
    name_col: str = 'Country_Name',
    region_col: str = 'Country_Region'
) -> Dict[int, str]:
    """
    Reads country IDs and names from a CSV file and returns them as a dictionary.

    Args:
        filepath: Path to the CSV file.
        id_col: Name of the column containing the numeric country IDs.
        name_col: Name of the column containing the country names.

    Returns:
        A dictionary where keys are country IDs (int) and values
        are country names (str). Returns an empty dictionary if an error occurs.
    """
    logging.info(f"Attempting to read country codes from: {filepath}")
    country_codes_dict: Dict[int, str] = {}
    country_region_dict: Dict[int, str] = {}
    
    try:
        # 1. Check if the file exists
        if not os.path.exists(filepath):
            logging.error(f"Codes file does not exist at path: {filepath}")
            return country_codes_dict # Return empty dictionary

        # 2. Read the CSV file using pandas
        # Assuming the separator might be semicolon for some CSVs, adjust if needed
        df_codes = pd.read_csv(filepath, sep=',') # Adjust separator if necessary

        # 3. Check if the required columns exist
        if id_col not in df_codes.columns:
            logging.error(f"ID column '{id_col}' not found in {filepath}")
            return country_codes_dict
        if name_col not in df_codes.columns:
            # Warning if the name column doesn't exist, but we can still proceed with IDs
            logging.warning(f"Name column '{name_col}' not found in {filepath}. Will use IDs only as names.")
            # We could decide to return only a list of IDs or a dict with None values
            # For now, we'll continue trying to create the dictionary, but names will be missing/placeholders.

        # 4. Create the dictionary {ID: CountryName}
        for index, row in df_codes.iterrows():
            try:
                # Try converting ID to integer
                country_id = int(row[id_col])
                # Get name, use ID as placeholder if name column doesn't exist or is empty/NaN
                # Check explicitly for the column's existence again before accessing
                if name_col in df_codes.columns and pd.notna(row[name_col]):
                     country_name = str(row[name_col])
                else:
                     country_name = f"Country_{country_id}" # Use placeholder if name is unavailable


                if country_id in country_codes_dict:
                     # Warning for duplicate ID, will overwrite with the last occurrence
                     logging.warning(f"Duplicate country ID found ({country_id}). It will be overwritten by the last entry in the CSV.")
                country_codes_dict[country_id] = country_name.strip()

            except (ValueError, TypeError) as conv_err:
                # Warning for error processing a row, skip this row
                logging.warning(f"Error processing row {index+1}: ID '{row[id_col]}' or Name '{row.get(name_col, 'N/A')}'. Skipping row. Error: {conv_err}")
                continue # Skip this row if conversion fails
        
        # 5. Create the dictionary {ID: CountryRegion}
        for index, row in df_codes.iterrows():
            try:
                country_id = int(row[id_col])
                country_region = str(row[region_col])
                country_region_dict[country_id] = country_region.strip()
            except (ValueError, TypeError) as conv_err:
                # Warning for error processing a row, skip this row
                logging.warning(f"Error processing row {index+1}: ID '{row[id_col]}' or Region '{row.get(region_col, 'N/A')}'. Skipping row. Error: {conv_err}")
                continue # Skip this row if conversion fails

        if country_codes_dict:
            logging.info(f"Successfully loaded {len(country_codes_dict)} country codes from {filepath}.")
        else:
             logging.warning(f"No valid codes were loaded from {filepath}.")
        
        if country_region_dict:
            logging.info(f"Successfully loaded {len(country_region_dict)} country regions from {filepath}.")
        else:
            logging.warning(f"No valid regions were loaded from {filepath}.")

    except pd.errors.EmptyDataError:
        logging.error(f"The CSV file {filepath} is empty.")
    except Exception as e:
        logging.error(f"Unexpected error while reading or processing the CSV file {filepath}: {e}")
        # Return empty dictionary in case of serious error
        return {}, {}

    return country_codes_dict, country_region_dict

# --- Example usage (should be removed or moved to tests or main.py) ---
# if __name__ == "__main__":
#     # Make sure 'data' directory and 'codigos.csv' exist for testing
#     test_file_path = '../data/codigos.csv' # Adjust path if running utils.py directly
#
#     # Create dummy directory and file if they don't exist for testing
#     if not os.path.exists(os.path.dirname(test_file_path)):
#         os.makedirs(os.path.dirname(test_file_path))
#     if not os.path.exists(test_file_path):
#         # Assuming 'NombrePais' is the actual column name in the CSV for names
#         dummy_df = pd.DataFrame({'ID': [572, 1566, 9999], 'NombrePais': ['Afghanistan', 'Chile', 'TestCountry']})
#         dummy_df.to_csv(test_file_path, index=False, sep=';') # Use semicolon for consistency
#         print(f"Dummy file created at {test_file_path}")
#
#     # Pass the correct name_col parameter if it's 'NombrePais' in the CSV
#     codes = get_country_codes_dict_from_csv(test_file_path, name_col='NombrePais')
#     if codes:
#         print("Codes loaded:")
#         print(codes)
#     else:
#         print("Could not load codes.")