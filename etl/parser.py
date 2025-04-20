import logging
from bs4 import BeautifulSoup
import pandas as pd # For timestamps
from typing import List, Dict, Optional

# Basic logging configuration (can be moved to config.py or initialized in main.py)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_lc_data(html_content: str, country_id: int, country_name: str, country_region: str) -> List[Dict]:
    """
    Parses the HTML content of a country's analysis page to extract LC data.

    Args:
        html_content: The HTML content of the page as a string.
        country_id: The ID of the current country (to include in the data).
        country_name: The name of the current country (to include in the data).

    Returns:
        A list of dictionaries, where each dictionary contains the extracted
        data for one LC. Returns an empty list if no data is found or
        if an error occurs during parsing.
    """
    df: pd.DataFrame = pd.DataFrame()
    if not html_content:
        logging.warning(f"Empty HTML content for {country_id} ('{country_name}'), cannot parse.")
        return df

    try:
        soup = BeautifulSoup(html_content, 'lxml') # Using 'lxml' is generally faster and more robust
                                                # Make sure it's installed (pip install lxml)

        # --- Debug: Print parsed HTML (optional, useful for debugging selectors) ---
        # Uncomment the next line if you need to see the formatted HTML
        #print(f"HTML Prettified for {country_id}:\n{soup.prettify()}")
        #with open('pagina_prettified.html', 'w', encoding='utf-8') as f:
        #    f.write(soup.prettify())
        # --- End Debug ---

        # --------------------------------------------------------------------
        # --- YOUR EXTRACTION LOGIC HERE! --- 
        # --------------------------------------------------------------------
        # You need to inspect the HTML of an actual analysis page
        # (e.g., https://core.aiesec.org.eg/analytics/1566/LC25/)
        # and find the correct CSS or XPath selectors for:
        #
        # 1. The main container for each LC (e.g., a table row <tr>, a div <div>)
        # 2. Within each LC container, the specific elements for:
        #    - LC Name
        #    - Program (oGTa, oGTe, etc.) - If applicable at the LC level or elsewhere
        #    - Number of Approvals
        #    - Number of Realizations
        #    - Number of Completions
        #    - Any other relevant data you see


        # Find all elements representing an LC (e.g., table rows)
        # Encuentra la tabla por ID
        tabla = soup.find('table', id='signups-table')
        if not tabla:
            raise ValueError(f"No se encontró una tabla con id='signups-table'")

        # Extrae filas con datos (td)
        filas = tabla.find_all('tr')
        datos = []

        for fila in filas:
            celdas = fila.find_all('td')
            if celdas:
                datos.append([celda.get_text(strip=True) for celda in celdas])

        # Crear el DataFrame sin encabezados
        df = pd.DataFrame(datos)
        
        # añadir columna con el nombre del pais al principio
        df.insert(0, 'Country_Name', country_name)
        df.insert(1, 'Country_Region', country_region)
        
        #logging.info(df)

        # Check if the DataFrame is empty
        if df.empty:
            logging.warning(f"No LC elements found using the specified selector for {country_id} ('{country_name}'). Check selectors in parser.py.")
            # It might be normal for a country to have no listed LCs, or the selector might be incorrect.
            return pd.DataFrame()

        logging.info(f"Found {len(df)} potential LC elements for {country_id} ('{country_name}'). Processing...")

        # --------------------------------------------------------------------
        # --- END OF YOUR EXTRACTION LOGIC --- 
        # --------------------------------------------------------------------

    except Exception as e_main:
        logging.error(f"General error during HTML parsing for {country_id} ('{country_name}'): {e_main}", exc_info=True)
        # Return empty list in case of severe error during initial parsing
        return pd.DataFrame()

    return df
