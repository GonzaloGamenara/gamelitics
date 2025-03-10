import sqlite3
import pandas as pd
import numpy as np

# Conectar a la base de datos SQLite
conectar = sqlite3.connect("videojuegos_analysis.db")

# Cargar los datos en un DataFrame
cargado = pd.read_sql_query("SELECT * FROM videojuegos", conectar)

# Cerrar la conexión
conectar.close()

print(f"Filas antes de limpiar: {cargado.shape[0]}") #muestra las filas

print(f"duplicados: {cargado.duplicated().sum()}") #muestra filas duplicadas

cargado.drop_duplicates(inplace=True) #eliminar duplicados

print(f"Filas limpias: {cargado.shape[0]}")

print(cargado.isnull().sum()) 

print(f"Filas con 'metacritic' nulas: {cargado['metacritic'].isnull().sum()}")
cargado.dropna(subset=["metacritic"], inplace=True)

cargado.fillna({"precio":0}, inplace=True)

print(cargado.isnull().sum())

print(cargado.shape[0])

cargado.reset_index(drop=True, inplace=True)

print(cargado["negative_rating_steam"].duplicated().sum())

cargado.drop_duplicates(subset=["negative_rating_steam"], inplace=True)

