import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urlparse

class conect_estudios():
    def __init__(self):
        self.response = []
        self.tags = []
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'}
        self._url_request = 'https://snies.mineducacion.gov.co/portal/ESTADISTICAS/Bases-consolidadas'
        self._url_base = 'https://snies.mineducacion.gov.co/1778'
        self._save_path = './data/Excel_Min' # modificar path para almacenamiento de archivos
        self.url_list_links = {}

    def set_url_request(self, url):
        self._url_request = url

    def set_url_base(self, url):
        self._url_base = url
        
    def set_save_path(self, path):
        self._save_path = path

    def make_reques(self):
        try:
            response = requests.get(self._url_request)
        except:
            print('No se pudo conectar a la url\n{}'.format(self._url_request))
        if response.status_code == 200:
            self.response = response
        else:
            print('Error en la conexión\nCódigo {}'.format(response.status_code))
    
    def make_soup(self):
        self.response = BeautifulSoup(markup = self.response.content, features = 'html.parser')

    def get_tags(self, tag):
        self.tags = self.response.find_all(name = tag)

    def lista_links(self):
        urls = []
        names = []
        for tag in self.tags:
            try:
                titulo = tag['title']
                name = titulo.split(' ')
                name.remove('a')
                name.remove('Ir')
            except:
                pass
            try:                
                if ('Estudiantes' in titulo) and (('Graduados' in titulo) or ('Admitidos' in titulo) or ('Matriculados' in titulo)) and (('2023' in titulo) or ('2024' in titulo)):
                    urls.append(self._url_base + '/' + tag['href'])
                    name = ' '.join(tuple(name))
                    names.append(name)
            except:
                pass
        self.url_list_links = {'url': urls, 'name': names}

    def download_excel_files(self):
        # Crear directorio si no existe
        os.makedirs(self._save_path, exist_ok=True)
        for _ in range(len(self.url_list_links['url'])):
            try:
                # Obtener nombre del archivo desde la URL
                filename = self.url_list_links['name'][_]+ '.xlsx'
                file_path = os.path.join(self._save_path, filename)
                # Saltar si ya existe
                if os.path.exists(file_path):
                    print(f"El archivo {filename} ya existe, omitiendo...")
                    continue
                print(f"Descargando {filename}...")
                # Hacer la petición
                response = requests.get(
                    self.url_list_links['url'][_], headers=self.header, stream=True)
                response.raise_for_status()  # Verificar errores HTTP
                # Guardar archivo
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Descarga completada: {file_path}\n")
            except Exception as e:
                print(f"Error al descargar {self.url_list_links['url'][_]}: {str(e)}\n")

    def crear_DataFrame(self):
        archivos = os.listdir(path = self._save_path)
        for _ in archivos:
            excel_file = pd.ExcelFile(path_or_buffer = self._save_path+'/'+_)
            hojas_validas = [
                hoja for hoja in excel_file.sheet_names if hoja not in ['ÍNDICE']]
            for sheet in hojas_validas:
                df = pd.read_excel(io=self._save_path + '/' + _,
                                   sheet_name = sheet, skiprows = 5)
                _ = _.split('.')[0]
                df.to_csv(path_or_buf = self._save_path + '/' + _ + '.csv', sep = ',')

    def get_data(self):
        self.make_reques()
        self.make_soup()
        self.get_tags(tag='a')
        self.lista_links()
        self.download_excel_files()
        self.crear_DataFrame()


conn = conect_estudios()
conn.get_data()
