import pandas as pd
import logging
import os
from typing import Dict, Optional # Para type hints

# Configuración básica de logging (puedes moverla a config.py o main.py si prefieres centralizarla)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_country_codes_dict_from_csv(
    filepath: str,
    id_col: str = 'ID',
    name_col: str = 'NombrePais'
) -> Dict[int, str]:
    """
    Lee los IDs y nombres de países desde un archivo CSV y los devuelve como un diccionario.

    Args:
        filepath: Ruta al archivo CSV.
        id_col: Nombre de la columna que contiene los IDs numéricos de país.
        name_col: Nombre de la columna que contiene los nombres de los países.

    Returns:
        Un diccionario donde las claves son los IDs de país (int) y los valores
        son los nombres de país (str). Devuelve un diccionario vacío si ocurre un error.
    """
    logging.info(f"Intentando leer códigos de país desde: {filepath}")
    country_codes_dict: Dict[int, str] = {}

    try:
        # 1. Verificar si el archivo existe
        if not os.path.exists(filepath):
            logging.error(f"El archivo de códigos no existe en la ruta: {filepath}")
            return country_codes_dict # Devuelve diccionario vacío

        # 2. Leer el archivo CSV usando pandas
        df_codes = pd.read_csv(filepath, sep=';')

        # 3. Verificar si las columnas requeridas existen
        if id_col not in df_codes.columns:
            logging.error(f"La columna ID '{id_col}' no se encontró en {filepath}")
            return country_codes_dict
        if name_col not in df_codes.columns:
            # Advertencia si la columna de nombre no existe, pero aún podemos proceder con IDs
            logging.warning(f"La columna de nombre '{name_col}' no se encontró en {filepath}. Se usarán solo IDs.")
            # Podríamos decidir devolver solo una lista de IDs o un diccionario con valores None
            # Por ahora, seguiremos intentando crear el diccionario, pero los nombres faltarán.

        # 4. Crear el diccionario {ID: NombrePais}
        for index, row in df_codes.iterrows():
            try:
                # Intentar convertir ID a entero
                country_id = int(row[id_col])
                # Obtener nombre, usar ID como placeholder si la columna de nombre no existe o está vacía
                country_name = str(row[name_col]) if name_col in df_codes.columns and pd.notna(row[name_col]) else f"País_{country_id}"

                if country_id in country_codes_dict:
                     logging.warning(f"ID de país duplicado encontrado ({country_id}). Se sobrescribirá con la última aparición en el CSV.")
                country_codes_dict[country_id] = country_name.strip()

            except (ValueError, TypeError) as conv_err:
                logging.warning(f"Error al procesar fila {index+1}: ID '{row[id_col]}' o Nombre '{row.get(name_col, 'N/A')}'. Saltando fila. Error: {conv_err}")
                continue # Saltar esta fila si la conversión falla

        if country_codes_dict:
            logging.info(f"Se cargaron exitosamente {len(country_codes_dict)} códigos de país desde {filepath}.")
        else:
             logging.warning(f"No se cargaron códigos válidos desde {filepath}.")

    except pd.errors.EmptyDataError:
        logging.error(f"El archivo CSV {filepath} está vacío.")
    except Exception as e:
        logging.error(f"Error inesperado al leer o procesar el archivo CSV {filepath}: {e}")
        # Devolver diccionario vacío en caso de error grave
        return {}

    return country_codes_dict

# --- Ejemplo de uso (se quitaría o movería a tests o main.py) ---
# if __name__ == "__main__":
#     # Asegúrate de que el directorio 'data' y el archivo 'codigos.csv' existan para probar
#     test_file_path = '../data/codigos.csv' # Ajusta la ruta si ejecutas utils.py directamente
#
#     # Crear directorio y archivo dummy si no existen para prueba
#     if not os.path.exists(os.path.dirname(test_file_path)):
#         os.makedirs(os.path.dirname(test_file_path))
#     if not os.path.exists(test_file_path):
#         dummy_df = pd.DataFrame({'ID': [572, 1566, 9999], 'NombrePais': ['Afghanistan', 'Chile', 'TestCountry']})
#         dummy_df.to_csv(test_file_path, index=False)
#         print(f"Archivo dummy creado en {test_file_path}")
#
#     codes = get_country_codes_dict_from_csv(test_file_path)
#     if codes:
#         print("Códigos cargados:")
#         print(codes)
#     else:
#         print("No se pudieron cargar los códigos.")