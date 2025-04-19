# AIESEC Core Dashboard Scraper

## Objective

This project aims to extract performance data for AIESEC Local Committees (LCs) from the AIESEC Egypt National Dashboard (`https://core.aiesec.org.eg/`). The extracted data is structured for subsequent analysis and visualization.

## Project Structure

```
aiesec_scraper/
├── data/               # Stores input (codigos.csv) and output (aiesec_lc_data_output.csv) data
├── logs/               # Log files (if configured)
├── src/                # Source code
│   ├── __init__.py
│   ├── config.py       # Configurations and constants
│   ├── parser.py       # HTML parsing and data extraction logic
│   ├── processing.py   # Data cleaning and standardization functions (Planned)
│   ├── scraper.py      # Main scraper class (HTTP requests, orchestration)
│   └── utils.py        # Utility functions (reading CSV, saving data, etc.)
├── tests/              # Tests
│   └── test_scraper_functional.py # Basic functional test
├── .env                # Environment variables (Optional)
├── requirements.txt    # Project dependencies
├── README.md           # This file
└── main.py             # Program entry point
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd aiesec_scraper
    ```
2.  **Create a virtual environment:** (Recommended)
    ```bash
    python -m venv venv
    # Activate the virtual environment
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Prepare the country codes file:**
    *   Create a file named `codigos.csv` inside the `data/` directory.
    *   This file must contain at least the columns `Country_ID` (with the numeric country ID) and `Country_Name` (with the country name), matching the defaults in `src/config.py`. Example using comma as separator:
        ```csv
        Country_ID,Country_Name
        572,Afghanistan
        1566,Chile
        ...
        ```
    *   *Note: Ensure the separator used in your CSV matches the one expected by `pd.read_csv` in `src/utils.py` (currently comma).* 

## Usage

1.  **Run the Scraper:**
    ```bash
    python main.py
    ```
    The extracted and processed data will be saved to `data/aiesec_lc_data_output.csv` (using a semicolon separator by default, as defined in `src/config.py`).

2.  **Run Functional Test:** To verify that the scraper can make requests and the main loop works (even without real data parsing implemented yet):
    ```bash
    python tests/test_scraper_functional.py
    ```

## Main Components (`src/`)

*   **`config.py`**: Centralizes configuration settings like base URLs, file paths, column names, headers, delays, and logging settings.
*   **`scraper.py`**: Contains the `AIESECScraper` class, which manages the `requests` session, fetches country pages, and orchestrates the process by calling the parser.
*   **`parser.py`**: Contains the `parse_lc_data` function using `BeautifulSoup` to analyze the HTML of each country page and extract relevant LC information into a pandas DataFrame. **(Note: Specific extraction logic still needs implementation based on HTML structure).**
*   **`utils.py`**: Includes utility functions like `get_country_codes_dict_from_csv` for reading the country codes CSV.
*   **`processing.py`**: (Planned) Intended to house functions for cleaning, standardizing, and transforming the final combined DataFrame obtained from the scraper (e.g., `process_data`).
