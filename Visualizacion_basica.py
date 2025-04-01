import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar el archivo Excel
file_path = 'C:/Users/Ali/Documents/GitHub/proyecto_ETL/Datos Consolidados.xlsx'
df = pd.read_excel(file_path)

# Mostrar información general del dataset
print("Información del dataset:")
df.info()

# Identificar columnas no numéricas
df_numeric = df.select_dtypes(include=['number'])

# Mostrar estadísticas descriptivas solo de columnas numéricas
print("\nEstadísticas descriptivas:")
print(df_numeric.describe())

# Visualizar valores nulos
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
plt.title("Mapa de valores nulos")
plt.show()

# Histograma de todas las variables numéricas
df_numeric.hist(figsize=(12, 10), bins=30)
plt.suptitle("Distribución de variables numéricas")
plt.show()

# Boxplots para visualizar outliers
plt.figure(figsize=(12, 6))
sns.boxplot(data=df_numeric, orient="h")
plt.title("Boxplot de variables numéricas")
plt.show()

# Matriz de correlación
plt.figure(figsize=(10, 8))
sns.heatmap(df_numeric.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title("Matriz de correlación")
plt.show()

# Gráficos de dispersión para analizar relaciones entre algunas variables
sns.pairplot(df_numeric)
plt.show()
