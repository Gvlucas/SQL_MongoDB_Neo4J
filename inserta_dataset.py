from pymongo import MongoClient
from pymongo.database import Database
import pymysql
from configuracion import *
from load_data import *

# inserta_dataset.py
# Autores: Gonzalo Velasco y Lucía Lozano
# Proyecto Bases de Datos - Inserción de nuevo dataset (Sports and Outdoors)

conexion_mysql = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )

CONNECTION_STRING = MONGO_CONFIG2['host']
client = MongoClient(CONNECTION_STRING)
db_mongo = client[MONGO_CONFIG2["database"]]

if __name__ == "__main__":
    
    try:
        cursor = conexion_mysql.cursor()

        for categoria, ruta in PATHS2.items():
                
                nombre_coleccion = MONGO_CONFIG2['collections'][categoria]
                coleccion_mongo = db_mongo[nombre_coleccion]
                
                insert_datos_mysql_mongo(categoria, ruta, cursor, coleccion_mongo)

        conexion_mysql.close()
        print("\nPROCESO DE CARGA FINALIZADO CON ÉXITO.")

    except Exception as e:
        print(f"ERROR CRÍTICO EN EL PROCESO DE CARGA: {e}") 
