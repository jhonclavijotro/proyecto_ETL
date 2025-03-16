from bs4 import BeautifulSoup
import requests
from io import BytesIO
import pandas as pd


dataframes_por_hoja = {}
response = requests.get("https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos")  # Cambia "URL_DE_LA_PAGINA" por la URL específica
base_url = "https://www.dane.gov.co"

if response.status_code == 200:
    # Crear el objeto BeautifulSoup para analizar el contenido de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Imprimir todos los enlaces encontrados en la página para depuración
    links = soup.find_all('a', href=True)

    excel_links = [link['href'] for link in links if (
            ('Anexo' in link.text or 'Anexos desestacionalizados' in link.text) and
            (link['href'].endswith('.xlsx') or link['href'].endswith('.xls')) and
            ("2025" in link['href'] or "2026" in link['href'] or "2027" in link['href'])
    # Filtrar años a partir de 2025
    )]
    # Imprimir resultados
    print("Enlaces filtrados:")
    if excel_links:
        for excel_link in excel_links:
            print(f"Enlace encontrado: {excel_link}")
    else:
        print("No se encontraron enlaces que coincidan con los criterios.")

    # Procesar cada enlace filtrado (si hay)
    for i, relative_link in enumerate(excel_links):
        excel_url = base_url + relative_link
        excel_response = requests.get(excel_url)
        archivo_excel = BytesIO(excel_response.content)
        excel_file = pd.ExcelFile(archivo_excel)
        hojas_validas = [hoja for hoja in excel_file.sheet_names if hoja not in ['Ficha Metodológica', 'Índice']]
        for hoja in hojas_validas:
            df_total_nacional = pd.read_excel(archivo_excel, sheet_name=hoja, skiprows=13)
            # Encontrar todas las posiciones donde aparece la palabra "Concepto" en la primera columna
            indices_concepto = df_total_nacional[
                df_total_nacional.iloc[:, 0].astype(str).str.strip() == "Concepto"].index
            # Lista para almacenar los DataFrames de esta hoja
            dataframes = []
            for i, posicion_concepto in enumerate(indices_concepto):
                # Verificar si la fila tiene valores vacíos para decidir encabezados
                encabezados_fila1 = df_total_nacional.iloc[posicion_concepto]
                encabezados_fila2 = df_total_nacional.iloc[posicion_concepto + 1]

                # Crear los encabezados finales evaluando columna por columna con acceso seguro usando `iloc`
                nuevos_encabezados = [
                    f"{encabezados_fila1.iloc[col]} {encabezados_fila2.iloc[col]}" if pd.notna(
                        encabezados_fila1.iloc[col]) else
                    encabezados_fila2.iloc[col]
                    for col in range(len(encabezados_fila1))
                ]

                # Determinar el inicio de los datos después de los encabezados
                inicio_datos = posicion_concepto + 2

                # Si no es el último "Concepto", cortar hasta la próxima posición
                if i + 1 < len(indices_concepto):
                    fin_datos = indices_concepto[i + 1]
                else:
                    fin_datos = len(df_total_nacional)  # Hasta el final del DataFrame

                # Crear un nuevo DataFrame para esta sección
                nuevo_dataframe = df_total_nacional.iloc[inicio_datos:fin_datos].copy()
                nuevo_dataframe.columns = nuevos_encabezados
                nuevo_dataframe.reset_index(drop=True, inplace=True)

                # Agregar el DataFrame a la lista
                dataframes.append(nuevo_dataframe)

            # Almacenar los DataFrames de esta hoja
            dataframes_por_hoja[hoja] = dataframes


else:
    print(f'Error al acceder a la página web: {response.status_code}')

print(dataframes_por_hoja)