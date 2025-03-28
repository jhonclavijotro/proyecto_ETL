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
        # modificar path para almacenamiento de archivos
        self._save_path = './data/Excel_Min'
        self.url_list_links = {}

    def set_url_request(self, url):
        """Función para setear la url de request"""
        self._url_request = url

    def set_url_base(self, url):
        """Función para setear la url base para 
        las descargas de los archivos"""
        self._url_base = url

    def set_save_path(self, path):
        """Función para setear el path para guardar
        los archivos y para leerlos a futuro"""
        self._save_path = path

    def make_reques(self):
        """Función para realizar el request
        de la pagina objetivo"""
        try:
            response = requests.get(self._url_request)
        except:
            print('No se pudo conectar a la url\n{}'.format(self._url_request))
        if response.status_code == 200:
            self.response = response
        else:
            print('Error en la conexión\nCódigo {}'.format(response.status_code))

    def make_soup(self):
        """Función que retorna el contenido del response
        en formato html usando BeautifulSoup"""
        self.response = BeautifulSoup(
            markup=self.response.content, features='html.parser')

    def get_tags(self, tag):
        """Función para recolectar las etiquetas objetivo"""
        self.tags = self.response.find_all(name=tag)

    def lista_links(self):
        """Función para extraer los links de descarga"""
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
        """Descarga de los links generados"""
        # Crear directorio si no existe
        os.makedirs(self._save_path, exist_ok=True)
        for _ in range(len(self.url_list_links['url'])):
            try:
                # Obtener nombre del archivo desde la URL
                filename = self.url_list_links['name'][_] + '.xlsx'
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
                print(
                    f"Error al descargar {self.url_list_links['url'][_]}: {str(e)}\n")
    
    def modificar_excel(self):
        """Lectura de los archivos .xlsx, eliminación de filas
        de encabezado para su posterior almacenamiento"""
        archivos = os.listdir(path = self._save_path)
        for _ in archivos:
            excel_file = pd.ExcelFile(path_or_buffer = self._save_path+'/'+_)
            hojas_validas = [
                hoja for hoja in excel_file.sheet_names if hoja not in ['ÍNDICE']]
            for sheet in hojas_validas:
                df = pd.read_excel(io = self._save_path + '/' + _,
                                   sheet_name = sheet, skiprows = 5)
                _ = _.split('.')[0]
                df.to_csv(path_or_buf = self._save_path +
                          '/' + _ + '.csv', sep = ',')

    def clean_files(self):
        """Elimina los archivos .xlsx que se descargan
        que son copia de los .csv"""
        archivos = os.listdir(path=self._save_path)
        for _ in archivos:
            if 'primer' in _.split('.')[0]:
                try:
                    name = _.split('.')[0].replace('Matriculados', '')
                    data = pd.read_csv(filepath_or_buffer=self._save_path + '/' + _)
                    data = data.drop(columns='Unnamed: 0')
                    data.to_csv(path_or_buf=self._save_path + '/' + name + '.csv')
                    os.remove(path=self._save_path + '/' + _)
                except:
                        os.remove(path=self._save_path + '/' + _)
            else:
                try:
                    if _.split('.')[1] == 'csv':
                        data = pd.read_csv(
                            filepath_or_buffer=self._save_path+'/'+_)
                        data = data.drop(columns='Unnamed: 0')
                        os.remove(path=self._save_path+'/'+_)
                        data.to_csv(path_or_buf=self._save_path+'/'+_)
                    elif _.split('.')[1] == 'xlsx':
                        os.remove(path=self._save_path+'/'+_)
                except Exception as e:
                    print(e)


    def call_admitidos(self):
        """Función que retorna un dataframe con la información
        de los estudiantes admitidos"""
        archivos = os.listdir(path=self._save_path)
        for archivo in archivos:
            try:
                if 'Admitidos' in archivo.split('.')[0]:
                    data = pd.read_csv(
                        filepath_or_buffer=self._save_path + '/' + archivo)
                    data.drop(columns='Unnamed: 0', inplace=True)
                    campos = data.columns()
                    return [data, campos]
                else:
                    pass
            except Exception as e:
                print('error: {}'.format(e))
    
    def call_graduados(self):
        """Función que retorna un dataframe con la información
        de los estudiantes graduados"""
        archivos = os.listdir(path=self._save_path)
        for archivo in archivos:
            try:
                if 'Graduados' in archivo.split('.')[0]:
                    data = pd.read_csv(
                        filepath_or_buffer=self._save_path + '/' + archivo)
                    data.drop(columns='Unnamed: 0', inplace=True)
                    campos = data.columns()
                    return [data, campos]
                else:
                    pass
            except Exception as e:
                print('error: {}'.format(e))
    
    def call_matriculados(self):
        """Función que retorna un dataframe con la información
        de los estudiantes matriculados"""
        archivos = os.listdir(path=self._save_path)
        for archivo in archivos:
            try:
                if 'Matriculados' in archivo.split('.')[0]:
                    data = pd.read_csv(
                        filepath_or_buffer=self._save_path + '/' + archivo)
                    data.drop(columns='Unnamed: 0', inplace=True)
                    campos = data.columns()
                    return [data, campos]
                else:
                    pass
            except Exception as e:
                print('error: {}'.format(e))

    def call_primer(self):
        """Función que retorna un dataframe con la información
        de los estudiantes matriculados en el primer periodo"""
        archivos = os.listdir(path=self._save_path)
        for archivo in archivos:
            try:
                if 'primer' in archivo.split('.')[0]:
                    data = pd.read_csv(
                        filepath_or_buffer=self._save_path + '/' + archivo)
                    data.drop(columns='Unnamed: 0', inplace=True)
                    campos = data.columns()
                    return [data, campos]
                else:
                    pass
            except Exception as e:
                print('error: {}'.format(e))
    
    def get_data(self):
        """Función que realiza la rutina de descarga
        de los archivos objetivo"""
        self.make_reques()
        self.make_soup()
        self.get_tags(tag='a')
        self.lista_links()
        self.download_excel_files()

    def clean_data(self):
        """Función que realiza la rutina de adecuar
        los archivos descargados para un formato más cómodo"""
        self.modificar_excel()
        self.clean_files()

