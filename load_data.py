#CARGADO DE LOS DATOS Y CREACIÓN DE BASES DE DATOS A MongoDB Y A MySQL - Gonzalo Velasco Lucas y Lucía Lozano Isac

import json
from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
import pymysql
from configuracion import *
import time


conexion_mysql = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password']
    )

def create_databases() -> Database:
    """
        Funcion para crear la base de datos de MongoDB y MySQL
        :return: conexión MySQL, BBDD MongoDB
    """

    # Creamos la BBDD de MySQL
    cursor = conexion_mysql.cursor()
    cursor.execute(f'DROP DATABASE IF EXISTS {MYSQL_CONFIG['database']}')
    sql = "CREATE DATABASE " + str(MYSQL_CONFIG["database"]) #Creamos la database eliminándola si existía anteriormente
    cursor.execute(sql)
    sql = "USE " + str(MYSQL_CONFIG["database"])
    cursor.execute(sql)

    # Creamos una sola vez la tabla Reviews 
    cursor.execute("""
        CREATE TABLE Reviews (
            reviewerID VARCHAR(50),
            asin VARCHAR(50),
            reviewerName VARCHAR(255),
            overall TINYINT NOT NULL,
            reviewTime DATE NOT NULL,
            categoria VARCHAR(50),
            PRIMARY KEY (reviewerID, asin)
        )
    """)

    # Creamos la BBDD de MongoDB
    CONNECTION_STRING = MONGO_CONFIG['host']
    client = MongoClient(CONNECTION_STRING)
    db_mongo = client[MONGO_CONFIG["database"]]
    
    print(f"Bases de Datos '{MYSQL_CONFIG['database']}' y '{MONGO_CONFIG['database']}' creadas.")

    return conexion_mysql,db_mongo

def insert_datos_mysql_mongo(categoria,path,cursor,coleccion_mongo)->None:
    """
        Función para insertar los datos en función del fichero a la
        colleción de MongoDB o a la table Reviews de MySQL 
        :return: None
    """
    print(f"Iniciando carga de {categoria}")
    batch_sql = []
    batch_mongo = []
    tam_max = 5000 #Tam. max batches

    with open(path, 'r', encoding='utf-8') as f:
        for linea in f: # Lectura línea a línea para ahorrar RAM
            try:
                data = json.loads(linea)

                #Convertimos fecha a formato strptime
                fecha_sucia = data.get("reviewTime")
                #Nos quedamos solo con día, mes y año
                fecha_limpia = datetime.strptime(fecha_sucia,'%m %d, %Y').date()

                #PROCEDEMOS A REPARTIR LA INFORMACIÓN TAL Y COMO SE ESPECIFICÓ EN EL INFORME
                datos_sql = (data.get('reviewerID'),
                            data.get('asin'),
                            data.get('reviewerName'),
                            data.get('overall'),
                            fecha_limpia,
                            categoria)
                datos_mongo = {"reviewerID":data.get('reviewerID'),
                                "asin":data.get('asin'),
                                "reviewText":data.get('reviewText'),
                                "summary":data.get('summary'),
                                "helpful":data.get('helpful')}
                
                batch_sql.append(datos_sql) #Añadimos datos a los batches
                batch_mongo.append(datos_mongo)

                if len(batch_sql)>= tam_max:
                    #Procedemos a inserción de los datos
                    cursor.executemany(f'INSERT IGNORE INTO Reviews (reviewerID,asin,reviewerName,overall,reviewTime,categoria) ' \
                    'VALUES (%s,%s,%s,%s,%s,%s)', batch_sql)
                    conexion_mysql.commit() # Aseguramos los datos
                    #En MongoDB cargamos todo de golpe
                    coleccion_mongo.insert_many(batch_mongo)
                    
                    # Vaciamos para las próximas 5000
                    batch_sql = []
                    batch_mongo = []
            except Exception as e:
                print(f"Error en línea: {e}") 
                continue

        if batch_sql:
            cursor.executemany(f'INSERT IGNORE INTO Reviews (reviewerID,asin,reviewerName,overall,reviewTime,categoria) ' \
            'VALUES (%s,%s,%s,%s,%s,%s)', batch_sql)
            conexion_mysql.commit() # Aseguramos los datos
            #En MongoDB cargamos todo de golpe
            coleccion_mongo.insert_many(batch_mongo)


                
if __name__ == "__main__":
    try:
    # Obtenemos la conexión de MySQL y la Base de Datos de MongoDB
        conexion_mysl,db_mongo = create_databases()
        cursor = conexion_mysql.cursor()

        for categoria, ruta in PATHS.items():
                # Obtenemos el nombre de la colección y la creamos en la BBDD
                nombre_coleccion = MONGO_CONFIG['collections'][categoria]
                coleccion_mongo = db_mongo[nombre_coleccion]
                
                # Insertamos los datos del fichero correspondiente
                insert_datos_mysql_mongo(categoria, ruta, cursor, coleccion_mongo)

        conexion_mysql.close()
        print("\nPROCESO DE CARGA FINALIZADO CON ÉXITO.")

    except Exception as e:
        print(f"ERROR CRÍTICO EN EL PROCESO DE CARGA: {e}") 
    

#Eficiencia del proceso asegurada; 
# · Tiempo aproximado en creación bases y cargado de datos: 25 segundos

