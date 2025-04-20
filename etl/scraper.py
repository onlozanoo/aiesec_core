import requests
import logging
import time
from typing import Dict, Optional, List
import pandas as pd # Import pandas
# from tqdm import tqdm # Keep console tqdm as fallback if needed
from tqdm.tk import tqdm as tqdm_tk # Import tqdm GUI version

# --- Import parsing function ---
from .parser import parse_lc_data # Relative import

# Assuming config.py will exist in the same directory (src)
# from .config import BASE_URL, DEFAULT_VIEW_SUFFIX, HEADERS, REQUEST_DELAY_SECONDS

# Basic logging configuration (can be moved to config.py or initialized in main.py)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIESECScraper:
    """
    Main class to handle scraping the AIESEC dashboard.

    Manages the requests session, sends requests to the analysis pages
    for each country, and coordinates data extraction by calling the parser.
    """

    def __init__(self):
        """
        Initializes the scraper by creating a persistent requests session
        and loading necessary configurations.
        """
        self.session = requests.Session()
        # Load configuration directly (or from config.py)
        from config import BASE_URL, DEFAULT_VIEW_SUFFIX, REQUEST_DELAY_SECONDS, HEADERS
        self.base_url = BASE_URL
        self.view_suffix = DEFAULT_VIEW_SUFFIX
        self.delay = REQUEST_DELAY_SECONDS
        self.session.headers.update(HEADERS)

        logging.info("Scraper initialized with a new session and configuration.")

    def fetch_country_page(self, country_id: int) -> Optional[str]:
        """
        Fetches the HTML content of the analysis page for a given country.

        Args:
            country_id: The numeric ID of the country to scrape.

        Returns:
            The HTML content of the page as a string if the request is successful,
            None in case of a network error.
        """
        # Construct URL making sure there are no double slashes
        country_url = f"{self.base_url.rstrip('/')}/{country_id}/{self.view_suffix.lstrip('/')}"
        logging.info(f"Accessing: {country_url}")
        try:
            response = self.session.get(country_url, timeout=20) # Increased timeout just in case
            response.raise_for_status() # Check for HTTP errors (4xx or 5xx)

            logging.debug(f"Successful request for Country ID {country_id}. Size: {len(response.content)} bytes.")
            # Return content as text for BeautifulSoup
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for Country ID {country_id}: {e}")
            return None
        except Exception as e:
            # Generic catch for other potential request-time errors
            logging.error(f"Unexpected error during request for Country ID {country_id}: {e}")
            return None

    def run_scraper(self, country_codes_dict: Dict[int, str], country_region_dict: Dict[int, str]) -> pd.DataFrame:
        """
        Orchestrates the entire scraping process for the given list of countries.

        Iterates over the country dictionary, fetches the HTML for each,
        calls the parsing function (from parser.py), and concatenates the results
        into a single DataFrame.

        Args:
            country_codes_dict: Dictionary {country_id: country_name}.

        Returns:
            A pandas DataFrame containing the combined extracted data for all LCs
            from all successfully scraped countries.
        """
        # Initialize an empty DataFrame to store all results
        all_extracted_data_df = pd.DataFrame()
        total_countries = len(country_codes_dict)
        logging.info(f"Starting scraping for {total_countries} countries...")

        # Wrap the iterator with tqdm for a GUI progress bar window
        progress_bar = tqdm_tk(country_codes_dict.items(), total=total_countries, desc="Scraping Countries", unit="country")

        for i, (country_id, country_name) in enumerate(progress_bar):
            # Optional: Update progress bar description with current country
            progress_bar.set_description(f"Scraping {country_name[:15]:<15}") # Pad name for consistent width

            # Log progress using English identifiers (INFO level might interfere less with tqdm)
            # logging.info(f"Processing Country {i+1}/{total_countries}: ID={country_id}, Name='{country_name}', Region='{country_region_dict[country_id]}'")

            # 1. Fetch HTML
            html_content = self.fetch_country_page(country_id)

            if html_content:
                # 2. Parse HTML by calling the external function
                try:
                    # --- ACTUAL CALL TO THE PARSING FUNCTION ---
                    # Expecting a DataFrame from parse_lc_data now
                    parsed_df = parse_lc_data(html_content, country_id, country_name, country_region_dict[country_id])
                    # --- END OF CALL ---

                    # Check if the parser returned a valid, non-empty DataFrame
                    if isinstance(parsed_df, pd.DataFrame) and not parsed_df.empty:
                        num_rows = len(parsed_df)
                        logging.info(f"Parsing successful for {country_id}. Found {num_rows} LCs.")
                        # Concatenate the new DataFrame to the main one
                        all_extracted_data_df = pd.concat([all_extracted_data_df, parsed_df], ignore_index=True)
                        #logging.info(all_extracted_data_df)
                    elif isinstance(parsed_df, pd.DataFrame) and parsed_df.empty:
                        logging.warning(f"Parsing returned an empty DataFrame for {country_id} ('{country_name}').")
                    else:
                         # Handle cases where parser might not return a DataFrame as expected
                         logging.error(f"Parsing function did not return a DataFrame for {country_id} ('{country_name}'). Type received: {type(parsed_df)}")

                except Exception as e:
                    logging.error(f"Unexpected error calling parsing function for {country_id} ('{country_name}'): {e}", exc_info=True)

            else:
                logging.warning(f"Could not fetch HTML for {country_id} ('{country_name}'). Skipping country.")

            # 3. Wait before the next request
            if i < total_countries - 1:
                 logging.debug(f"Waiting {self.delay} seconds before next country...")
                 time.sleep(self.delay)

        # Log final summary with total rows collected
        total_rows_collected = len(all_extracted_data_df)
        logging.info(f"Scraping completed. Extracted data for {total_rows_collected} total rows across all countries.")
        return all_extracted_data_df

    def close_session(self):
        """Closes the requests session."""
        if self.session:
            self.session.close()
            logging.info("Requests session closed.")

# --- Example of how it would be used from main.py (remove or move to tests) ---
# if __name__ == "__main__":
#     # This would simulate running from main.py
#     from utils import get_country_codes_dict_from_csv # Assuming utils is at the same level
#
#     # Create dummy directory and file if they don't exist for testing
#     test_file_path = '../data/codigos.csv'
#     # Ensure the dummy data creation uses the expected column names if changed in utils.py
#     dummy_csv_data = {'ID': [1566, 572], 'NombrePais': ['Chile', 'Afghanistan']} # Example data
#     if not os.path.exists(os.path.dirname(test_file_path)):
#         os.makedirs(os.path.dirname(test_file_path))
#     if not os.path.exists(test_file_path):
#         import pandas as pd # Need pandas here for dummy creation
#         dummy_df = pd.DataFrame(dummy_csv_data)
#         dummy_df.to_csv(test_file_path, index=False, sep=';') # Match separator used in utils
#         print(f"Dummy file created at {test_file_path}")
#
#     # Load codes using the function from utils
#     # Make sure name_col matches the one expected by get_country_codes_dict_from_csv
#     country_codes = get_country_codes_dict_from_csv(test_file_path, name_col='NombrePais')
#
#     if country_codes:
#         scraper_instance = AIESECScraper()
#         # The actual parser implementation is missing here
#         # For now, run_scraper will return an empty DataFrame because parsing is a placeholder
#         results = scraper_instance.run_scraper(country_codes)
#         print(f"\nScraping results (simulated): {len(results)} LCs found.")
#         # print(results) # Uncomment to see the empty DataFrame
#         scraper_instance.close_session()
#     else:
#         print("Could not load country codes to test the scraper.")
