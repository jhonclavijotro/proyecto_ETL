from bs4 import BeautifulSoup
import requests
from io import BytesIO
import pandas as pd
from pymongo import MongoClient

# Conexión a MongoDB Atlas
mongo_uri = "mongodb+srv://alimera:Bvb3FnOqQkzs7vpc@cluster0.kxv7p.mongodb.net/geih_database?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["geih_database"]

# Solicitud a la página
response = requests.get("https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos")
base_url = "https://www.dane.gov.co"

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)

    # Filtrar los enlaces para incluir solo los años 2025 y 2026
    excel_links = [
        link['href'] for link in links if (
            ('Anexo' in link.text or 'Anexos desestacionalizados' in link.text) and
            link['href'].endswith('.xlsx') and
            ("2025" in link['href'] or "2026" in link['href'])
        )
    ]

    # Iterar sobre los enlaces encontrados
    for excel_link in excel_links:
        excel_url = base_url + excel_link
        excel_response = requests.get(excel_url)
        archivo_excel = BytesIO(excel_response.content)
        excel_file = pd.ExcelFile(archivo_excel)

        # Procesar hojas válidas
        hojas_validas = [hoja for hoja in excel_file.sheet_names if hoja not in ['Ficha Metodológica', 'Índice']]
        for hoja in hojas_validas:
            df_total_nacional = pd.read_excel(archivo_excel, sheet_name=hoja, skiprows=13)
            indices_concepto = df_total_nacional[df_total_nacional.iloc[:, 0].astype(str).str.strip() == "Concepto"].index

            for i, posicion_concepto in enumerate(indices_concepto):
                encabezados_fila1 = df_total_nacional.iloc[posicion_concepto]
                encabezados_fila2 = df_total_nacional.iloc[posicion_concepto + 1]

                # Crear encabezados únicos para el DataFrame
                nuevos_encabezados = [
                    f"{encabezados_fila1.iloc[col]} {encabezados_fila2.iloc[col]}" if pd.notna(encabezados_fila1.iloc[col]) else encabezados_fila2.iloc[col]
                    for col in range(len(encabezados_fila1))
                ]

                # Asegurar que los encabezados sean únicos
                def make_unique(column_names):
                    seen = {}
                    for idx, col in enumerate(column_names):
                        if col not in seen:
                            seen[col] = 0
                        else:
                            seen[col] += 1
                            col = f"{col}_{seen[col]}"
                        column_names[idx] = col
                    return column_names

                nuevos_encabezados = make_unique(nuevos_encabezados)

                inicio_datos = posicion_concepto + 2
                fin_datos = indices_concepto[i + 1] if i + 1 < len(indices_concepto) else len(df_total_nacional)

                nuevo_dataframe = df_total_nacional.iloc[inicio_datos:fin_datos].copy()
                nuevo_dataframe.columns = nuevos_encabezados
                nuevo_dataframe.reset_index(drop=True, inplace=True)

                # Insertar en MongoDB
                collection_name = f"{hoja}_section_{i + 1}"
                db[collection_name].insert_many(nuevo_dataframe.to_dict("records"))

else:
    print(f"Error al acceder a la página web: {response.status_code}")
