import requests
from bs4 import BeautifulSoup
import pandas as pd


url = 'https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo/geih-historicos'
response = requests.get(url)
print(response)

if response.status_code == 200:
    # Crear el objeto BeautifulSoup para analizar el contenido de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar todos los enlaces a archivos Excel en la página
    links = soup.find_all('a', href=True)
    excel_links = [link['href'] for link in links if link['href'].endswith('.xlsx') or link['href'].endswith('.xls')]

    print(excel_links)
else:
    print(f'Error al acceder a la página web: {response.status_code}')
