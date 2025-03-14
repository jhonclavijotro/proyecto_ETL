import dataframes
import requests
from bs4 import BeautifulSoup
import pandas as pd

Excel = [] #variable para contenido de excel
# URL base de la página web
base_url = 'https://www.dane.gov.co'
# URL de la página web que contiene los enlaces a los archivos Excel
url = 'https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos'
response = requests.get(url)

#print(response)

if response.status_code == 200:
    # Crear el objeto BeautifulSoup para analizar el contenido de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos los enlaces a archivos Excel en la página
    links = soup.find_all('a', href=True)
    excel_links = [link['href'] for link in links if (('Anexo' in link.text or 'Anexos desestacionalizados' in link.text) and (link['href'].endswith('.xlsx') or link['href'].endswith('.xls')))]
    #print(excel_links)

    for i, relative_link in enumerate(excel_links):
        excel_url = base_url + relative_link
        excel_response = requests.get(excel_url)
        print(excel_url)
        print(excel_response)

else:
    print(f'Error al acceder a la página web: {response.status_code}')
