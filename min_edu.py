import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urlparse

class conect_estudios():
    def __init__(self):
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'}
        self._url_request = 'https://snies.mineducacion.gov.co/portal/ESTADISTICAS/Bases-consolidadas'
        self._url_base = 'https://snies.mineducacion.gov.co/1778'
        self._save_path = './data/Excel_Min' # modificar path para almacenamiento de archivos
        self.data = {}

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
            return response
        else:
            print('Error en la conexión\nCódigo {}'.format(response.status_code))

    def lista_links(self, tags):
        urls = []
        names = []
        for tag in tags:
            try:
                titulo = tag['title']
                if ('Estudiantes' in titulo) and (('Graduados' in titulo) or ('Admitidos' in titulo) or ('Matriculados' in titulo)) and (('2023' in titulo) or ('2024' in titulo)):
                    urls.append(self._url_base + '/' + tag['href'])
                    names.append(tag['title'])
            except:
                pass
        lista = {'url': urls, 'name': names}
        return lista

    def download_excel_files(self, urls, names):
        # Crear directorio si no existe
        os.makedirs(self._save_path, exist_ok=True)
        for _ in range(len(urls)):
            try:
                # Obtener nombre del archivo desde la URL
                filename = names[_] + '.xlsx'
                file_path = os.path.join(self._save_path, filename)
                # Saltar si ya existe
                if os.path.exists(file_path):
                    print(f"El archivo {filename} ya existe, omitiendo...")
                    continue
                print(f"Descargando {filename}...")
                # Hacer la petición
                response = requests.get(
                    urls[_], headers=self.header, stream=True)
                response.raise_for_status()  # Verificar errores HTTP
                # Guardar archivo
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"Descarga completada: {file_path}\n")
            except Exception as e:
                print(f"Error al descargar {urls[_]}: {str(e)}\n")

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
        response = self.make_reques()
        response = BeautifulSoup(response.content, features='html.parser')
        tags = response.find_all(name='a', href=True)
        lista = self.lista_links(tags=tags)
        return lista
