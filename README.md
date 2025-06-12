# AIESEC Core Dashboard Scraper

## Objective

This project aims to extract performance data for AIESEC Local Committees (LCs) from the AIESEC Egypt National Dashboard (`https://core.aiesec.org.eg/`). The extracted data is structured, processed, and saved (as Parquet files) for subsequent analysis and visualization, potentially in Power BI.

## Project Structure

```
aiesec_scraper/
├── data/               # Stores input (codigos.csv) and output (*.parquet) data
├── dashboard/          # Power BI dashboard files (e.g., dashboard_principal.pbix)
├── etl/                # ETL (Extract, Transform, Load) source code
│   ├── __init__.py
│   ├── config.py       # Configurations and constants
│   ├── extract_lcs.py  # Main ETL workflow function
│   ├── parser.py       # HTML parsing and data extraction logic
│   ├── processing.py   # Data cleaning, standardization, and grouping functions
│   ├── scraper.py      # Scraper class (HTTP requests)
│   └── utils.py        # Utility functions (reading CSV, etc.)
├── logs/               # Log files (if configured)
├── tests/              # Tests
│   └── test_scraper_functional.py # Basic functional test
├── .env                # Environment variables (Optional)
├── requirements.txt    # Project dependencies
├── README.md           # This file
└── update_data.py      # Main script to trigger the ETL process
```

## AIESEC Regions

*   Americas
*   Europe
*   Asia Pacific
*   MEA (Middle East & Africa)

## Roadmap

- [x] **Project Setup**: Define structure, dependencies (`requirements.txt`), basic README.
- [x] **Configuration**: Centralize settings in `etl/config.py`.
- [x] **Utilities (`etl/utils.py`)**: Implement function to read country codes from CSV.
- [x] **Scraper Core (`etl/scraper.py`)**: Implement `AIESECScraper` class for handling requests session, fetching pages per country ID, and orchestrating the scraping loop.
- [x] **HTML Parser (`etl/parser.py`)**: Implement `parse_lc_data` using BeautifulSoup to extract data from HTML tables into a DataFrame.
- [x] **ETL Workflow (`etl/extract_lcs.py`)**: Define main `extract_all_data` function orchestrating load -> scrape -> process.
- [x] **Data Processing (`etl/processing.py`)**: Implement basic data processing structure and program grouping function (`group_data_by_program`).
- [x] **Main Trigger Script (`update_data.py`)**: Create entry point to run ETL, save results as Parquet (timestamped & latest), optionally open Power BI.
- [x] **Progess Bar**: Create a simple GUI progress bar that allows to see how the scraping process advance. 
- [ ] **Data Cleaning & Standardization**: Enhance `etl/processing.py` with robust cleaning logic (type conversion, handling missing values, column renaming/selection).
- [ ] **GUI**: Creation of a GUI that allows to personalize the update of the countries.
- [ ] **Saving Results**: Refine saving logic if needed (currently in `update_data.py`).
- [ ] **Dashboard / Visualization**: Develop Power BI dashboard (`dashboard/dashboard_principal.pbix`) connecting to `data/data_latest.parquet`.
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
    venv\Scripts\activate.bat
    # macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt 
    ```
4.  **Prepare the country codes file:**
    *   Create a file named `codigos.csv` inside the `data/` directory (or modify the filename in `etl/config.py`).
    *   Ensure this file contains the columns defined in `etl/config.py` (`COUNTRY_ID_COLUMN` and `COUNTRY_NAME_COLUMN`, currently 'Country_ID' and 'Country_Name').
    *   Example using comma separator:
        ```csv
        Country_ID,Country_Name
        572,Afghanistan
        1566,Chile
        ...
        ```
    *   *Note: Ensure the separator used in your CSV matches the one expected by `pd.read_csv` in `etl/utils.py`.* 
5.  **(Optional) Place Power BI File:**
    *   Create a `dashboard/` directory.
    *   Place your Power BI file (e.g., `dashboard_principal.pbix`) inside it if you want the script to open it automatically.

## Usage

1.  **Run the Data Update Process:**
    ```bash
    python update_data.py
    ```
    *   This script orchestrates the entire process defined in `etl/extract_lcs.py`.
    *   It saves the final DataFrame in the `data/` directory as:
        *   `data_<YYYYMMDD_HHMMSS>.csv` (timestamped version)
        *   `data_latest.csv` (overwritten each run)
    *   Optionally attempts to open the Power BI file specified in the script (`dashboard/dashboard_principal.pbix`).

2.  **Run Functional Test:** To verify basic scraper operation (requires adjustments for `etl` structure):
    ```bash
    # (Test script tests/test_scraper_functional.py needs updates 
    #  to reflect the change from src to etl and potentially import changes)
    python tests/test_scraper_functional.py 
    ```

## Main Components (`etl/`)

*   **`config.py`**: Centralizes configuration settings (URLs, file paths, column names, delays, logging, etc.).
*   **`scraper.py`**: Defines the `AIESECScraper` class for managing web requests.
*   **`parser.py`**: Implements `parse_lc_data` using BeautifulSoup to extract data from HTML into a DataFrame.
*   **`utils.py`**: Contains utility functions (e.g., `get_country_codes_dict_from_csv`).
*   **`processing.py`**: Includes functions for data cleaning (`process_data`) and transformation (`group_data_by_program`).
*   **`extract_lcs.py`**: Contains the main `extract_all_data` function that orchestrates the ETL steps (calling utils, scraper, parser, processing).

## Dashboard Overview

The Power BI dashboard is the final visualization product of this project. It is built using the structured and processed data obtained through the ETL pipeline. The dashboard is designed to support Greener's IR (International Relations) efforts by offering two key views:

<img width="586" alt="Image" src="https://github.com/user-attachments/assets/7d0348fe-d779-42d3-936d-692ba6a06524"/>

### Dashboard Sections

* 1. Dashboard Países:
 
<img width="598" alt="Image" src="https://github.com/user-attachments/assets/7616c04e-a011-41f0-8e80-a8a6f1a30f9e" />

Aggregated view by country.

Allows for comparison of performance indicators between countries.

Useful for identifying top-performing countries for potential partnerships.



Key elements in this view:

Map visualization to show Approved EPs by country with intensity.

Top 3 LCs by Approved shown in horizontal bars.

Funnel Sankey Chart for program, region, and LC breakdown — helping identify contribution by level.

Global filters for region, country, program, and date.

* 2. Dashboard LCs:

Disaggregated view by Local Committee (LC).

Enables detailed tracking of funnel performance for each LC.

Supports data-driven decisions when selecting IR partners.

Preview

https://app.powerbi.com/view?r=eyJrIjoiMjQyZmMwZTYtMDU2Mi00YzA0LTk2ZGMtNWU4MWZlMjZlMmYyIiwidCI6IjNiOTQ0ZDlhLTEwNTEtNDY4NS1iMDlkLTlhOTVlZTJkYmQ5OSIsImMiOjR9&pageName=30a7448ebaea2647b4d3&pageName=b094782ddb6122e4434f

This cover represents the homepage of the dashboard where users can choose which section (Países or LCs) they want to explore.

The dashboard connects dynamically to data/data_latest.csv and is updated automatically every time the ETL process is executed using update_data.py.
