import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


class ConectEstudios:
    def __init__(self):
        self.session = requests.Session()
        self.response = None
        self.header = {'User-Agent': 'Mozilla/5.0'}
        self._url_request = 'https://snies.mineducacion.gov.co/portal/ESTADISTICAS/Bases-consolidadas'
        self._url_base = 'https://snies.mineducacion.gov.co/1778'
        self._save_path = os.path.join(os.getcwd(), "data", "Excel_Min")
        os.makedirs(self._save_path, exist_ok=True)
        self.url_list_links = {}

    def make_request(self):
        """Realiza la solicitud HTTP a la página objetivo"""
        try:
            response = self.session.get(self._url_request, headers=self.header)
            response.raise_for_status()
            self.response = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f'Error en la conexión: {e}')

    def get_tags(self):
        """Extrae enlaces relevantes de la página"""
        tags = self.response.find_all('a')
        urls, names = [], []
        for tag in tags:
            try:
                titulo = tag.get('title', '')
                if any(word in titulo for word in ['Admitidos', 'Graduados', 'Matriculados']) and any(year in titulo for year in ['2023', '2024']):
                    urls.append(self._url_base + '/' + tag['href'])
                    names.append(titulo.replace("Ir a ", "").replace("a ", "").strip())
            except Exception:
                continue
        self.url_list_links = {'url': urls, 'name': names}

    def download_files(self):
        """Descarga los archivos de Excel"""
        for i, url in enumerate(self.url_list_links['url']):
            filename = f"{self.url_list_links['name'][i]}.xlsx"
            file_path = os.path.join(self._save_path, filename)
            if os.path.exists(file_path):
                print(f"El archivo {filename} ya existe, omitiendo...")
                continue
            try:
                print(f"Descargando {filename}...")
                response = self.session.get(url, headers=self.header, stream=True)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Descarga completada: {filename}")
            except requests.RequestException as e:
                print(f"Error al descargar {filename}: {e}")

    def process_files(self):
        """Convierte los archivos Excel en CSV, eliminando encabezados innecesarios"""
        archivos = [f for f in os.listdir(self._save_path) if f.endswith('.xlsx')]
        for archivo in archivos:
            try:
                file_path = os.path.join(self._save_path, archivo)
                df = pd.read_excel(file_path, skiprows=5)
                csv_path = file_path.replace('.xlsx', '.csv')
                df.to_csv(csv_path, index=False)
                os.remove(file_path)  # Elimina el archivo original de Excel
                print(f"Convertido {archivo} a CSV")
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")

    def load_data(self, keyword):
        """Carga y devuelve un DataFrame basado en el tipo de archivo (Admitidos, Graduados, etc.)"""
        archivos = [f for f in os.listdir(self._save_path) if keyword in f and f.endswith('.csv')]
        for archivo in archivos:
            try:
                df = pd.read_csv(os.path.join(self._save_path, archivo))
                return df, df.columns.tolist()
            except Exception as e:
                print(f"Error cargando {archivo}: {e}")
        return None, []

    def get_data(self):
        """Ejecuta el flujo completo de descarga y procesamiento"""
        self.make_request()
        self.get_tags()
        self.download_files()

    def clean_data(self):
        """Ejecuta la limpieza de datos descargados"""
        self.process_files()


if __name__ == "__main__":
    conn = ConectEstudios()
    conn.get_data()
    conn.clean_data()
