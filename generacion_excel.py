import os
import requests
from bs4 import BeautifulSoup
import re

# URL de la página web
url = "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos"
base_url = "https://www.dane.gov.co"

# Crear carpeta para guardar los archivos
output_folder = "archivos_GEIH"
os.makedirs(output_folder, exist_ok=True)

# Obtener la página web
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Buscar enlaces a archivos Excel
    links = soup.find_all('a', href=True)

    excel_links = []
    date_pattern = re.compile(r'(\w+)-?(\d{4})')  # Captura "feb2025" o "feb-2025"

    for link in links:
        href = link['href']
        if href.endswith('.xlsx') or href.endswith('.xls'):
            match = date_pattern.search(href)
            if match:
                month, year = match.groups()
                excel_links.append((href, int(year), month))

    # Diccionario de meses
    month_order = {
        'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
    }

    # Filtrar archivos con fechas válidas
    excel_links = [(link, year, month) for link, year, month in excel_links if month.lower()[:3] in month_order]

    if excel_links:
        # Ordenar por año y mes
        latest_files = sorted(excel_links, key=lambda x: (x[1], month_order[x[2].lower()[:3]]), reverse=True)

        # Encontrar ambos archivos del mes más reciente
        latest_month_year = (latest_files[0][1], latest_files[0][2])
        selected_files = [file for file in latest_files if (file[1], file[2]) == latest_month_year]

        print("\n✅ **Descargando archivos más recientes:**")
        for file in selected_files:
            file_url = base_url + file[0]
            file_name = file[0].split("/")[-1]  # Extraer el nombre del archivo
            file_path = os.path.join(output_folder, file_name)

            # Descargar el archivo
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(file_response.content)
                print(f"✔️ Guardado: {file_path}")
            else:
                print(f"❌ Error al descargar: {file_url}")
    else:
        print("\n⚠️ No se encontraron archivos con fechas válidas.")
else:
    print("❌ No se pudo acceder a la página.")
