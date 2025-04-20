# AIESEC Core Dashboard Scraper

## Objective

This project aims to extract performance data for AIESEC Local Committees (LCs) from the AIESEC Egypt National Dashboard (`https://core.aiesec.org.eg/`). The extracted data is structured, processed, and saved for subsequent analysis and visualization.

## Project Structure

```
aiesec_scraper/
├── data/               # Stores input (codigos.csv) and output (aiesec_lc_data_output.csv) data
├── logs/               # Log files (if configured)
├── src/                # Source code
│   ├── __init__.py
│   ├── config.py       # Configurations and constants
│   ├── parser.py       # HTML parsing and data extraction logic
│   ├── processing.py   # Data cleaning, standardization, and grouping functions
│   ├── scraper.py      # Main scraper class (HTTP requests, orchestration)
│   └── utils.py        # Utility functions (reading CSV, etc.)
├── tests/              # Tests
│   └── test_scraper_functional.py # Basic functional test
├── .env                # Environment variables (Optional)
├── requirements.txt    # Project dependencies
├── README.md           # This file
└── main.py             # Program entry point
```

## AIESEC Regions

*(Please add the list of AIESEC operational regions here)*

*   Americas
*   Europe
*   Asia Pacific
*   MEA (Middle East & Africa)

## Roadmap

- [x] **Project Setup**: Define structure, dependencies (`requirements.txt`), basic README.
- [x] **Configuration**: Centralize settings in `src/config.py`.
- [x] **Utilities (`src/utils.py`)**: Implement function to read country codes from CSV.
- [x] **Scraper Core (`src/scraper.py`)**: Implement `AIESECScraper` class for handling requests session, fetching pages per country ID, and orchestrating the scraping loop.
- [x] **HTML Parser (`src/parser.py`)**: Implement `parse_lc_data` using BeautifulSoup to extract data from HTML tables into a DataFrame.
- [x] **Main Script (`main.py`)**: Create entry point, handle imports, orchestrate workflow (load codes -> scrape -> process -> save).
- [x] **Data Processing (`src/processing.py`)**: Implement basic data processing structure and program grouping function (`group_data_by_program`).
- [ ] **Data Cleaning & Standardization**: Enhance `src/processing.py` with robust cleaning logic (type conversion, handling missing values, column renaming/selection).
- [ ] **Saving Results**: Implement a robust saving function (potentially in `utils.py` or `main.py`) for the final DataFrame.
- [ ] **Dashboard / Visualization**: Develop dashboards or visualizations based on the cleaned data.
- [ ] **Error Handling & Logging**: Enhance error handling and logging throughout the application.
- [ ] **Unit/Integration Tests**: Add more comprehensive tests for parser, processing, and scraper logic.

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
    *   Create a file named `codigos.csv` inside the `data/` directory (or modify the filename in `src/config.py`).
    *   Ensure this file contains the columns defined in `src/config.py` (`COUNTRY_ID_COLUMN` and `COUNTRY_NAME_COLUMN`, currently 'Country_ID' and 'Country_Name').
    *   Example using comma separator:
        ```csv
        Country_ID,Country_Name
        572,Afghanistan
        1566,Chile
        ...
        ```
    *   *Note: Ensure the separator used in your CSV matches the one expected by `pd.read_csv` in `src/utils.py`.* 

## Usage

1.  **Run the Scraper:**
    ```bash
    python main.py
    ```
    *   The script reads country codes from `data/codigos.csv`.
    *   It scrapes the data for each country, parsing the HTML tables.
    *   The combined raw data is potentially processed/cleaned by functions in `src/processing.py`.
    *   The final DataFrame is saved to `data/aiesec_lc_data_output.csv` (default path and separator defined in `src/config.py`).

2.  **Run Functional Test:** To verify basic scraper operation (requests, looping):
    ```bash
    python tests/test_scraper_functional.py
    ```

## Main Components (`src/`)

*   **`config.py`**: Centralizes configuration settings (URLs, file paths, column names, delays, logging, etc.).
*   **`scraper.py`**: Defines the `AIESECScraper` class responsible for managing the web scraping session, fetching pages, and coordinating the overall scraping workflow by calling the parser.
*   **`parser.py`**: Implements the `parse_lc_data` function. It uses `BeautifulSoup` to parse the HTML content of a country page and extracts data (currently targeting tables with specific IDs/structures) into a pandas DataFrame.
*   **`utils.py`**: Contains utility functions, primarily `get_country_codes_dict_from_csv` for reading the input country codes.
*   **`processing.py`**: Contains functions for post-scraping data manipulation, such as `process_data` for cleaning and `group_data_by_program` for grouping the final DataFrame by AIESEC program.
