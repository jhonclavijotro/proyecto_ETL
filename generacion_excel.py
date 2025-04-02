import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def descargar_GEIH():
    # URLs base
    url = "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos"
    base_url = "https://www.dane.gov.co"

    # Crear carpeta para guardar los archivos descargados
    output_folder = "archivos_GEIH"
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Descargar contenido de la página principal
        response = requests.get(url)
        response.raise_for_status()  # Manejar posibles errores de la solicitud

        # Parsear el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)

        # Patrón para identificar fechas en los nombres de archivos
        excel_links = []
        date_pattern = re.compile(r'(\w+)-?(\d{4})')

        for link in links:
            href = link['href']
            if href.endswith(('.xlsx', '.xls')):  # Verificar extensiones de archivo
                match = date_pattern.search(href)
                if match:
                    month, year = match.groups()
                    excel_links.append((href, int(year), month))

        # Ordenar enlaces según el mes y año más recientes
        month_order = {
            'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
        }

        excel_links = [
            (link, year, month) for link, year, month in excel_links
            if month.lower()[:3] in month_order
        ]

        if excel_links:
            # Seleccionar los archivos más recientes
            latest_files = sorted(
                excel_links,
                key=lambda x: (x[1], month_order[x[2].lower()[:3]]),
                reverse=True
            )
            latest_month_year = (latest_files[0][1], latest_files[0][2])
            selected_files = [
                file for file in latest_files if (file[1], file[2]) == latest_month_year
            ]

            # Descargar los archivos seleccionados
            for file in selected_files:
                file_url = base_url + file[0]
                file_name = file[0].split("/")[-1]
                file_path = os.path.join(output_folder, file_name)

                try:
                    file_response = requests.get(file_url)
                    file_response.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(file_response.content)
                    print(f"[{datetime.now()}] Descargado: {file_name}")
                except requests.RequestException as e:
                    print(f"[{datetime.now()}] Error al descargar {file_name}: {e}")
    except requests.RequestException as e:
        print(f"[{datetime.now()}] Error al acceder a la página principal: {e}")

if __name__ == "__main__":
    descargar_GEIH()