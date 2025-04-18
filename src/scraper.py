import requests
import logging
import time
from typing import Dict, Optional, List

# --- Importar la función de parseo ---
from parser import parse_lc_data # Asegúrate que parser.py esté en src/

# Asumiendo que config.py existirá en el mismo directorio (src)
# from .config import BASE_URL, DEFAULT_VIEW_SUFFIX, HEADERS, REQUEST_DELAY_SECONDS

# Configuración básica de logging (puede moverse a config.py o inicializarse en main.py)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIESECScraper:
    """
    Clase principal para manejar el scraping del dashboard de AIESEC.

    Gestiona la sesión de requests, realiza peticiones a las páginas de análisis
    de cada país y coordina la extracción de datos llamando al parser.
    """

    def __init__(self):
        """
        Inicializa el scraper creando una sesión de requests persistente
        y cargando la configuración necesaria.
        """
        self.session = requests.Session()
        # Cargar configuración directamente (o desde config.py)
        self.base_url = "https://core.aiesec.org.eg/analytics/"
        self.view_suffix = "/LC25/"
        self.delay = 2 # O cargar desde config.py: from .config import REQUEST_DELAY_SECONDS
        default_user_agent = 'MyAIESECDataScraper/1.0 (Contact: your_email@example.com)' # O desde config.py

        self.session.headers.update({
            # Cargar User-Agent (o desde config.py: from .config import HEADERS)
            'User-Agent': default_user_agent
        })

        logging.info("Scraper inicializado con una nueva sesión y configuración.")

    def fetch_country_page(self, country_id: int) -> Optional[str]:
        """
        Obtiene el contenido HTML de la página de análisis para un país dado.

        Args:
            country_id: El ID numérico del país a scrapear.

        Returns:
            El contenido HTML de la página como string si la petición es exitosa,
            None en caso de error de red.
        """
        country_url = f"{self.base_url}{country_id}{self.view_suffix}"
        logging.info(f"Accediendo a: {country_url}")
        try:
            response = self.session.get(country_url, timeout=20)
            response.raise_for_status()
            
            logging.debug(f"Petición exitosa para Country ID {country_id}. Tamaño: {len(response.content)} bytes.")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error en la petición para Country ID {country_id}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error inesperado durante la petición para Country ID {country_id}: {e}")
            return None

    def run_scraper(self, country_codes_dict: Dict[int, str]) -> List[Dict]:
        """
        Orquesta el proceso completo de scraping para la lista de países dada.

        Itera sobre el diccionario de países, obtiene el HTML de cada uno,
        llama a la función de parseo (a implementar en parser.py) y
        acumula los resultados.

        Args:
            country_codes_dict: Diccionario {country_id: country_name}.

        Returns:
            Una lista de diccionarios, donde cada diccionario representa los datos
            extraídos para un LC (Local Committee).
        """
        all_extracted_data: List[Dict] = []
        total_countries = len(country_codes_dict)
        logging.info(f"Iniciando scraping para {total_countries} países...")

        for i, (country_id, country_name) in enumerate(country_codes_dict.items()):
            logging.info(f"Procesando País {i+1}/{total_countries}: ID={country_id}, Nombre='{country_name}'")

            # 1. Obtener el HTML
            html_content = self.fetch_country_page(country_id)

            if html_content:
                # 2. Parsear el HTML llamando a la función externa
                try:
                    # --- LLAMADA REAL A LA FUNCIÓN DE PARSEO ---
                    parsed_data = parse_lc_data(html_content, country_id, country_name)
                    # --- FIN DE LA LLAMADA ---

                    if parsed_data:
                        logging.info(f"Parseo exitoso para {country_id}. Se encontraron {len(parsed_data)} registros de LC.")
                        all_extracted_data.extend(parsed_data)
                    else:
                        # Esto puede ser normal si un país no tiene LCs o si el parseo no encuentra nada con los selectores actuales
                        logging.warning(f"El parseo no devolvió datos de LC válidos para {country_id} ('{country_name}').")

                except Exception as e:
                    # Capturar errores durante la llamada al parseo (inesperado si parse_lc_data maneja sus propios errores)
                    logging.error(f"Error inesperado al llamar a la función de parseo para {country_id} ('{country_name}'): {e}", exc_info=True)

            else:
                logging.warning(f"No se pudo obtener el HTML para {country_id} ('{country_name}'). Saltando país.")

            # 3. Esperar antes de la siguiente petición
            if i < total_countries - 1:
                 logging.debug(f"Esperando {self.delay} segundos antes del siguiente país...")
                 time.sleep(self.delay)

        logging.info(f"Scraping completado. Se extrajeron datos de {len(all_extracted_data)} LCs en total (basado en la lógica de parseo actual).")
        return all_extracted_data

    def close_session(self):
        """Cierra la sesión de requests."""
        if self.session:
            self.session.close()
            logging.info("Sesión de requests cerrada.")

# --- Ejemplo de cómo se usaría desde main.py (quitar o mover a tests) ---
# if __name__ == "__main__":
#     # Esto simularía la ejecución desde main.py
#     from utils import get_country_codes_dict_from_csv # Asumiendo que utils está en el mismo nivel
#
#     # Crear directorio y archivo dummy si no existen para prueba
#     test_file_path = '../data/codigos.csv'
#     if not os.path.exists(os.path.dirname(test_file_path)):
#         os.makedirs(os.path.dirname(test_file_path))
#     if not os.path.exists(test_file_path):
#         dummy_df = pd.DataFrame({'ID': [1566, 572], 'NombrePais': ['Chile', 'Afghanistan']}) # Ejemplo simple
#         dummy_df.to_csv(test_file_path, index=False)
#         print(f"Archivo dummy creado en {test_file_path}")
#
#     country_codes = get_country_codes_dict_from_csv(test_file_path)
#
#     if country_codes:
#         scraper_instance = AIESECScraper()
#         # Aquí faltaría la implementación real del parser
#         # Por ahora, run_scraper devolverá una lista vacía porque el parseo es un placeholder
#         results = scraper_instance.run_scraper(country_codes)
#         print(f"\nResultados del scraping (simulado): {len(results)} LCs encontrados.")
#         # print(results) # Descomentar para ver la lista vacía
#         scraper_instance.close_session()
#     else:
#         print("No se pudieron cargar los códigos de país para probar el scraper.")
