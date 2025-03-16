import pandas as pd
from io import BytesIO
import requests

# URL y descarga del archivo Excel
url = 'https://www.dane.gov.co/files/operaciones/GEIH/anex-GEIH-ene2025.xlsx'
response = requests.get(url)

# Cargar el archivo Excel en memoria
archivo_excel = BytesIO(response.content)

# Obtener los nombres de las hojas, excluyendo 'Ficha Metodológica' y 'Índice'
excel_file = pd.ExcelFile(archivo_excel)
hojas_validas = [hoja for hoja in excel_file.sheet_names if hoja not in ['Ficha Metodológica', 'Índice']]

# Lista para almacenar los DataFrames generados por hoja
dataframes_por_hoja = {}

# Iterar sobre cada hoja válida
for hoja in hojas_validas:
    df_total_nacional = pd.read_excel(archivo_excel, sheet_name=hoja, skiprows=13)

    # Encontrar todas las posiciones donde aparece la palabra "Concepto" en la primera columna
    indices_concepto = df_total_nacional[df_total_nacional.iloc[:, 0].astype(str).str.strip() == "Concepto"].index

    # Lista para almacenar los DataFrames de esta hoja
    dataframes = []

    # Iterar sobre cada posición de "Concepto" encontrada
    for i, posicion_concepto in enumerate(indices_concepto):
        # Verificar si la fila tiene valores vacíos para decidir encabezados
        encabezados_fila1 = df_total_nacional.iloc[posicion_concepto]
        encabezados_fila2 = df_total_nacional.iloc[posicion_concepto + 1]

        # Crear los encabezados finales evaluando columna por columna con acceso seguro usando `iloc`
        nuevos_encabezados = [
            f"{encabezados_fila1.iloc[col]} {encabezados_fila2.iloc[col]}" if pd.notna(encabezados_fila1.iloc[col]) else
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
