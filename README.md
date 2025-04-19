# AIESEC Core Dashboard Scraper

## Objetivo

Este proyecto tiene como objetivo extraer datos de rendimiento de los Comités Locales (LCs) de AIESEC desde el Dashboard Nacional de AIESEC en Egipto (`https://core.aiesec.org.eg/`). Los datos extraídos se estructuran para su posterior análisis y visualización.

## Estructura del Proyecto

```
aiesec_scraper/
├── data/               # Almacena datos de entrada (codigos.csv) y salida (aiesec_lc_data.csv)
├── logs/               # Archivos de registro (si se configuran)
├── src/                # Código fuente
│   ├── __init__.py
│   ├── scraper.py      # Clase principal del scraper (peticiones HTTP, orquestación)
│   ├── parser.py       # Funciones para parsear HTML (BeautifulSoup) y extraer datos
│   ├── utils.py        # Funciones auxiliares (leer CSV, guardar datos, etc.)
│   └── config.py       # Configuraciones y constantes (Aún no creado)
├── tests/              # Pruebas
│   └── test_scraper_functional.py # Prueba funcional básica
├── .env                # Variables de entorno (Opcional)
├── requirements.txt    # Dependencias del proyecto
├── README.md           # Este archivo
└── main.py             # Punto de entrada del programa (Aún no creado)

```

## Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd aiesec_scraper
    ```
2.  **Crear un entorno virtual:** (Recomendado)
    ```bash
    python -m venv venv
    # Activar el entorno virtual
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Preparar archivo de códigos:**
    *   Crea un archivo llamado `codigos.csv` dentro de la carpeta `data/`.
    *   Este archivo debe contener al menos las columnas `ID` (con el ID numérico del país) y `NombrePais` (con el nombre del país). Ejemplo:
        ```csv
        ID,NombrePais
        572,Afghanistan
        1566,Chile
        ...
        ```

## Uso

1.  **Ejecutar el Scraper:** (Una vez que `main.py` esté implementado)
    ```bash
    python main.py
    ```
    Los datos extraídos se guardarán (de forma incremental) en `data/aiesec_lc_data.csv`.

2.  **Ejecutar Prueba Funcional:** Para verificar que el scraper puede realizar peticiones y el bucle funciona (sin parseo real aún):
    ```bash
    python tests/test_scraper_functional.py
    ```

## Componentes Principales (`src/`)

*   **`scraper.py`**: Contiene la clase `AIESECScraper` que maneja la sesión de `requests`, realiza las peticiones a las URLs de cada país y llama al parser.
*   **`parser.py`**: Contiene la función `parse_lc_data` que utiliza `BeautifulSoup` para analizar el HTML de cada página de país y extraer la información relevante de los LCs. **(Nota: La lógica de extracción específica aún necesita ser implementada)**.
*   **`utils.py`**: Contiene funciones de utilidad como `get_country_codes_dict_from_csv` para leer los códigos de país del CSV y `save_data` (a implementar) para guardar los resultados.
*   **`config.py`**: (Pendiente) Centralizará constantes como URLs base, cabeceras, rutas de archivos, etc.
